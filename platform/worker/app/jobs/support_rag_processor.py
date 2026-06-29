"""
Support RAG Job Processor

Processes customer support queries using the SupportRAG DualStoreRAGPipeline.
Handles vector store initialization (load-from-disk or build), async queries
via the native aquery() method, Groq rate limiting, and full metrics collection.
"""

import json
import asyncio
import time
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import sys

# ---------------------------------------------------------------------------
# Path bootstrap: add SupportRAG root to sys.path so its `src` package is
# importable without installing it.  The layout is:
#   SupportRAG/                       ← SUPPORT_RAG_ROOT (added to sys.path)
#     src/
#       core/dual_rag_pipeline.py
#       config/settings.py
#     platform/worker/app/jobs/support_rag_processor.py  ← THIS FILE
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
SUPPORT_RAG_ROOT = _THIS_FILE.parents[5]  # parents[5] = SupportRAG/ repo root

if not SUPPORT_RAG_ROOT.exists():
    # Docker: SupportRAG is mounted at /supportrag
    _docker_path = Path("/supportrag")
    if _docker_path.exists():
        SUPPORT_RAG_ROOT = _docker_path
    else:
        # Last resort: try relative to cwd
        SUPPORT_RAG_ROOT = Path(os.getcwd()).parent / "SupportRAG"

if str(SUPPORT_RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(SUPPORT_RAG_ROOT))


# ---------------------------------------------------------------------------
# Groq Rate Limiter
# ---------------------------------------------------------------------------

class GroqRateLimiter:
    """
    Sliding-window rate limiter for the Groq API.

    Groq free-tier limits (llama-3.3-70b-versatile):
      - 30 requests / minute
      - 6 000 tokens / minute

    Adjust via worker settings: GROQ_QPS / GROQ_TOKENS_PER_MINUTE.
    """

    def __init__(self, requests_per_minute: int = 30, tokens_per_minute: int = 6000):
        self.rpm = requests_per_minute
        self.tpm = tokens_per_minute
        # Sliding windows store timestamps of past requests / tokens
        self._req_window: List[float] = []
        self._tok_window: List[tuple] = []   # (timestamp, token_count)
        self._lock = asyncio.Lock()

    async def acquire(self, estimated_tokens: int = 800) -> None:
        """
        Block until the request can proceed within rate limits.

        Waits in 100 ms increments rather than raising an error so callers
        don't need retry logic.
        """
        while True:
            async with self._lock:
                now = time.monotonic()
                window = 60.0  # 1 minute

                # Purge expired entries
                self._req_window = [t for t in self._req_window if now - t < window]
                self._tok_window = [(t, c) for t, c in self._tok_window if now - t < window]

                used_tokens = sum(c for _, c in self._tok_window)

                if (len(self._req_window) < self.rpm and
                        used_tokens + estimated_tokens <= self.tpm):
                    # Capacity available — record and proceed
                    self._req_window.append(now)
                    self._tok_window.append((now, estimated_tokens))
                    return  # ← exit the loop

            # Rate-limited — wait 100 ms before retrying
            await asyncio.sleep(0.1)

    def stats(self) -> Dict[str, int]:
        """Return current usage counters (best-effort, not locked)."""
        now = time.monotonic()
        window = 60.0
        reqs = sum(1 for t in self._req_window if now - t < window)
        toks = sum(c for t, c in self._tok_window if now - t < window)
        return {"requests_last_minute": reqs, "tokens_last_minute": toks}


# ---------------------------------------------------------------------------
# SupportRAGProcessor
# ---------------------------------------------------------------------------

class SupportRAGProcessor:
    """
    Async job processor wrapping DualStoreRAGPipeline.

    Lifecycle:
      - SupportRAGProcessor.initialize() is called ONCE at worker startup.
        It tries to load pre-built vector stores from disk; falls back to
        building them from the CSV/HuggingFace data if not found.
      - Each job calls process(job), which delegates to the pipeline's
        native aquery() for parallel FAQ + Ticket retrieval and async LLM.
    """

    # Class-level singletons shared across all processor instances
    _pipeline = None          # DualStoreRAGPipeline instance
    _rate_limiter: Optional[GroqRateLimiter] = None
    _initialized: bool = False
    _init_error: Optional[str] = None

    def __init__(self):
        """Lightweight instance init — all state is on the class."""
        pass

    # ------------------------------------------------------------------
    # Class-level initialisation (called once at worker startup)
    # ------------------------------------------------------------------

    @classmethod
    async def initialize(cls) -> None:
        """
        Initialize the RAG pipeline and vector stores.

        Strategy:
          1. Try to load pre-built stores from disk (fast path).
          2. If not found, build from source data (slow, ~minutes).
          3. Initialise the Groq rate limiter from worker settings.

        Raises on unrecoverable errors so the worker can log and decide
        whether to continue or abort.
        """
        if cls._initialized:
            return

        try:
            print("[SupportRAGProcessor] Bootstrapping - SupportRAG path:", SUPPORT_RAG_ROOT)

            # We must run SupportRAG from its own root so relative `data/`
            # paths in the pipeline resolve correctly.
            original_cwd = os.getcwd()
            os.chdir(str(SUPPORT_RAG_ROOT))

            try:
                from src.core.dual_rag_pipeline import DualStoreRAGPipeline
            finally:
                os.chdir(original_cwd)

            from app.core.config import get_worker_settings
            settings = get_worker_settings()

            # Build pipeline (stays chdir'd internally via data_dir = Path("data"))
            # We patch the pipeline's data_dir to an absolute path so chdir
            # gymnastics aren't needed at query time.
            os.chdir(str(SUPPORT_RAG_ROOT))
            try:
                pipeline = DualStoreRAGPipeline()
                # Override relative paths with absolutes
                pipeline.data_dir = SUPPORT_RAG_ROOT / "data"
                pipeline.logs_dir = SUPPORT_RAG_ROOT / "logs"
                pipeline.logs_dir.mkdir(exist_ok=True)

                # --- Load or build vector stores ---
                vector_store_dir = pipeline.data_dir / "vector_stores"
                faq_path   = vector_store_dir / "faq_store"
                ticket_path = vector_store_dir / "ticket_store"

                if faq_path.exists() and ticket_path.exists():
                    print("[SupportRAGProcessor] Loading pre-built vector stores from disk...")
                    pipeline.load_vector_stores()
                    print("[SupportRAGProcessor] Vector stores loaded successfully.")
                else:
                    print("[SupportRAGProcessor] Pre-built stores not found — building from data...")
                    loop = asyncio.get_event_loop()
                    use_ivf = getattr(settings, "use_vector_store_ivf", True)
                    await loop.run_in_executor(None, pipeline.build_vector_stores, use_ivf)
                    # Persist for next startup
                    await loop.run_in_executor(None, pipeline.save_vector_stores)
                    print("[SupportRAGProcessor] Vector stores built and saved.")

                cls._pipeline = pipeline
            finally:
                os.chdir(original_cwd)

            # --- Rate limiter ---
            rpm = getattr(settings, "groq_requests_per_minute", 30)
            tpm = getattr(settings, "groq_tokens_per_minute", 6000)
            cls._rate_limiter = GroqRateLimiter(
                requests_per_minute=rpm,
                tokens_per_minute=tpm,
            )
            print(f"[SupportRAGProcessor] Rate limiter: {rpm} req/min, {tpm} tokens/min")

            cls._initialized = True
            print("[SupportRAGProcessor] Initialization complete.")

        except Exception as exc:
            cls._init_error = str(exc)
            print(f"[SupportRAGProcessor] FATAL initialization error: {exc}")
            raise

    # ------------------------------------------------------------------
    # Per-job processing
    # ------------------------------------------------------------------

    async def process(self, job: Any) -> Dict[str, Any]:
        """
        Process a support_rag job.

        Expected job.payload keys:
          - question  (str, required) : the user's support question
          - top_k     (int, optional) : number of docs to retrieve (default 5)

        Returns a rich result dict with answer, citations, confidence,
        latency breakdown, token estimates, and rate-limit stats.
        """
        wall_start = time.monotonic()

        try:
            # ── Guard: pipeline must be initialised ──────────────────────────
            if not self._initialized:
                if self._init_error:
                    return self._error_result(
                        f"RAG pipeline failed to initialize: {self._init_error}",
                        "InitializationError",
                    )
                # Lazy init (fallback — normally init is done at startup)
                await self.initialize()

            # ── Parse payload ────────────────────────────────────────────────
            payload = self._extract_payload(job)
            question = payload.get("question", "").strip()
            top_k    = int(payload.get("top_k", 5))

            if not question:
                return self._error_result(
                    "Missing or empty 'question' in job payload.",
                    "ValidationError",
                )

            top_k = max(1, min(top_k, 20))  # clamp to [1, 20]

            # ── Rate limiting ────────────────────────────────────────────────
            # Estimate tokens: question words × 1.3 + ~600 for context/answer
            estimated_tokens = int(len(question.split()) * 1.3) + 600
            rl_start = time.monotonic()
            await self._rate_limiter.acquire(estimated_tokens=estimated_tokens)
            rl_wait_ms = round((time.monotonic() - rl_start) * 1000, 2)

            # ── Run async RAG query ──────────────────────────────────────────
            query_start = time.monotonic()
            result = await self._aquery_pipeline(question, top_k)
            query_ms = round((time.monotonic() - query_start) * 1000, 2)

            # ── Total wall time ──────────────────────────────────────────────
            total_ms = round((time.monotonic() - wall_start) * 1000, 2)

            # ── Build enriched response ──────────────────────────────────────
            pipeline_latency = result.get("latency_ms", 0.0)
            confidence       = result.get("confidence", 0.0)

            # Token estimates (pipeline doesn't track exact counts)
            query_tokens    = int(len(question.split()) * 1.3)
            response_tokens = int(len(result.get("answer", "").split()) * 1.3)

            return {
                "status":     "completed",
                "answer":     result.get("answer", ""),
                "source":     result.get("source", "unknown"),  # "FAQ" or "Ticket"
                "confidence": round(confidence, 4),
                "citations":  result.get("citations", []),
                # ── Latency breakdown ──────────────────────────────────────
                "latency_ms": total_ms,
                "metrics": {
                    "pipeline_latency_ms":    round(pipeline_latency, 2),
                    "rate_limit_wait_ms":     rl_wait_ms,
                    "worker_overhead_ms":     round(total_ms - pipeline_latency, 2),
                    "query_tokens_estimated": query_tokens,
                    "response_tokens_estimated": response_tokens,
                    "top_k_used":             top_k,
                    "rate_limiter_stats":     self._rate_limiter.stats(),
                },
                # ── Metadata ───────────────────────────────────────────────
                "query":     question,
                "job_id":    getattr(job, "id", None),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as exc:
            return self._error_result(str(exc), type(exc).__name__)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _aquery_pipeline(self, question: str, top_k: int) -> Dict[str, Any]:
        """
        Call pipeline.aquery() — which already runs parallel FAISS searches
        and async Groq LLM — then restore cwd afterwards.
        """
        original_cwd = os.getcwd()
        try:
            os.chdir(str(SUPPORT_RAG_ROOT))
            return await self._pipeline.aquery(question, top_k=top_k)
        finally:
            os.chdir(original_cwd)

    @staticmethod
    def _extract_payload(job: Any) -> Dict[str, Any]:
        """Safely extract the payload dict from a job object."""
        payload = getattr(job, "payload", {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                payload = {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _error_result(message: str, error_type: str) -> Dict[str, Any]:
        """Standardised error response."""
        return {
            "status":     "failed",
            "error":      message,
            "error_type": error_type,
            "failed_at":  datetime.now(timezone.utc).isoformat(),
        }
