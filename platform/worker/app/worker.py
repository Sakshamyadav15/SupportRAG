"""
Worker Main Module

The worker service that polls the job queue and processes jobs.
Runs as a separate process from the API service.
"""

import json
import asyncio
import signal
import sys
import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from app.core.config import get_worker_settings
from app.core.database import get_db_session
from app.core.redis import get_worker_redis
from app.jobs.processor import JobProcessorRegistry, ProcessorNotFoundError
from app.jobs.support_rag_processor import SupportRAGProcessor


settings = get_worker_settings()


# =============================================================================
# SQLAlchemy Models (mirrored from API service)
# =============================================================================

class Base(DeclarativeBase):
    """Base class for models."""
    pass


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class User(Base):
    """User model (mirrored from API service)."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

class Job(Base):
    """Job model (mirrored from API service)."""
    
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="data_processing", nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    result_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


# =============================================================================
# JobWrapper  — thin adapter between DB model and processor API
# =============================================================================

class JobWrapper:
    """Thin adapter exposing processor-friendly attributes from a DB Job row."""

    def __init__(self, job_db: Job):
        self.id     = job_db.id
        self.type   = job_db.type
        self.status = job_db.status
        self.payload = self._parse_payload(job_db.input_data)

    @staticmethod
    def _parse_payload(input_data: Optional[str]) -> dict:
        try:
            return json.loads(input_data or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}


# =============================================================================
# Worker Class
# =============================================================================

class Worker:
    """
    Job processing worker.

    Polls the Redis queue for jobs and processes them.
    Updates job status in PostgreSQL.
    Invalidates cache after processing.
    """

    def __init__(self):
        """Initialize worker."""
        self.worker_id    = settings.worker_id
        self.queue_name   = settings.job_queue_name
        self.poll_timeout = settings.queue_poll_timeout
        self.running      = False

        # A single event loop for the entire worker lifetime
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self.redis = get_worker_redis()

        print(f"[{self.worker_id}] Worker initialized")
        print(f"[{self.worker_id}] Queue: {self.queue_name}")
        print(f"[{self.worker_id}] Poll timeout: {self.poll_timeout}s")
        print(f"[{self.worker_id}] Available job types: {', '.join(JobProcessorRegistry.get_all_types())}")

    def start(self) -> None:
        """Start the worker main loop."""
        self.running = True
        print(f"[{self.worker_id}] Starting worker...")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT,  self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Initialize RAG processor (builds/loads vector stores once at startup)
        print(f"[{self.worker_id}] Initializing RAG processor...")
        try:
            self._loop.run_until_complete(SupportRAGProcessor.initialize())
            print(f"[{self.worker_id}] RAG processor initialized successfully.")
        except Exception as exc:
            print(f"[{self.worker_id}] WARNING: Failed to initialize RAG processor: {exc}")
            print(f"[{self.worker_id}] Continuing - errors will be surfaced per-job")

        self._run_loop()

    def stop(self) -> None:
        """Stop the worker gracefully."""
        print(f"[{self.worker_id}] Stopping worker...")
        self.running = False

    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals."""
        print(f"\n[{self.worker_id}] Received signal {signum}, shutting down...")
        self.stop()

    def _run_loop(self) -> None:
        """Main worker loop — synchronous poll + async dispatch."""
        print(f"[{self.worker_id}] Worker running. Waiting for jobs...")

        while self.running:
            try:
                message = self._dequeue_job()

                if message is None:
                    continue  # Poll timeout — keep looping

                job_id = message.get("job_id")
                if job_id:
                    # Run the async job processor on the persistent event loop
                    self._loop.run_until_complete(self._process_job(job_id))

            except Exception as exc:
                print(f"[{self.worker_id}] Error in main loop: {exc}")
                # Continue running despite errors

        print(f"[{self.worker_id}] Worker stopped")

    def _dequeue_job(self) -> Optional[dict]:
        """
        Dequeue a job from Redis.

        Returns:
            Job message dict or None if timeout / Redis unavailable
        """
        if not self.redis.is_available:
            print(f"[{self.worker_id}] Redis unavailable, waiting 5s...")
            import time
            time.sleep(5)
            return None

        result = self.redis.brpop([self.queue_name], timeout=self.poll_timeout)

        if result is None:
            return None

        try:
            _, message_str = result
            return json.loads(message_str)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"[{self.worker_id}] Failed to parse queue message: {exc}")
            return None

    async def _process_job(self, job_id: int) -> None:
        """
        Fetch, dispatch, and update a single job — fully async.

        Args:
            job_id: Job ID to process
        """
        print(f"[{self.worker_id}] Picked up job {job_id}")

        db = get_db_session()

        try:
            # ── Fetch job ────────────────────────────────────────────────────
            job = db.query(Job).filter(Job.id == job_id).first()

            if job is None:
                print(f"[{self.worker_id}] Job {job_id} not found in database")
                return

            job_type = getattr(job, "type", "support_rag")
            print(f"[{self.worker_id}] Job {job_id} | type={job_type}")

            # ── Mark PROCESSING ──────────────────────────────────────────────
            job.status     = JobStatus.PROCESSING
            job.updated_at = datetime.now(timezone.utc)
            db.commit()

            # ── Dispatch to processor ────────────────────────────────────────
            try:
                processor_class = JobProcessorRegistry.get_processor(job_type)
                processor       = processor_class()
                job_wrapper     = JobWrapper(job)

                result = await processor.process(job_wrapper)

                # ── Mark COMPLETED ───────────────────────────────────────────
                job.status      = JobStatus.COMPLETED
                job.result_data = json.dumps(result)
                job.updated_at  = datetime.now(timezone.utc)
                db.commit()

                latency = result.get("latency_ms", "?")
                source  = result.get("source", "?")
                conf    = result.get("confidence", "?")
                print(
                    f"[{self.worker_id}] Job {job_id} completed "
                    f"| latency={latency}ms | source={source} | confidence={conf}"
                )

            except ProcessorNotFoundError as exc:
                self._fail_job(db, job, str(exc), "ProcessorNotFoundError")
                print(f"[{self.worker_id}] Job {job_id} failed: {exc}")

            except Exception as exc:
                self._fail_job(db, job, str(exc), type(exc).__name__)
                print(f"[{self.worker_id}] Job {job_id} failed: {exc}")

            # ── Invalidate cache ─────────────────────────────────────────────
            self._invalidate_cache(job_id, job.user_id)

        except Exception as exc:
            print(f"[{self.worker_id}] Unexpected error processing job {job_id}: {exc}")
            db.rollback()

            # Best-effort: mark failed
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    self._fail_job(db, job, f"Worker error: {exc}", type(exc).__name__)
            except Exception as inner:
                print(f"[{self.worker_id}] Could not mark job {job_id} as failed: {inner}")

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fail_job(db, job: Job, error: str, error_type: str) -> None:
        """Write FAILED status and error payload to the DB."""
        job.status = JobStatus.FAILED
        job.result_data = json.dumps({
            "status":     "failed",
            "error":      error,
            "error_type": error_type,
            "failed_at":  datetime.now(timezone.utc).isoformat(),
        })
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

    def _invalidate_cache(self, job_id: int, user_id: int) -> None:
        """
        Invalidate Redis cache entries after job processing.

        Args:
            job_id:  Job ID
            user_id: User ID (for list-level cache invalidation)
        """
        if not settings.cache_enabled:
            return

        try:
            self.redis.delete(f"cache:job:{job_id}")
            print(f"[{self.worker_id}] Cache invalidated for job {job_id}")
        except Exception as exc:
            print(f"[{self.worker_id}] Cache invalidation failed: {exc}")


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Worker entry point."""
    print("=" * 60)
    print("Job Processing Worker — SupportRAG Edition")
    print("=" * 60)
    print(f"Database : {settings.database_url[:50]}...")
    print(f"Redis    : {settings.redis_url}")
    print(f"Queue    : {settings.job_queue_name}")
    print("=" * 60)

    worker = Worker()

    try:
        worker.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user (KeyboardInterrupt)")
    finally:
        worker.stop()
        print("Worker shutdown complete")


if __name__ == "__main__":
    main()
