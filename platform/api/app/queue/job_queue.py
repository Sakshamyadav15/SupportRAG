"""
Job Queue Module

Redis-backed job queue for async job processing.
Provides simple enqueue/dequeue operations with graceful degradation.
"""

import json
from typing import Optional, Any
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.redis import get_redis_client, RedisClient
from app.core.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()


class JobQueueError(Exception):
    """Base exception for job queue errors."""
    pass


class QueueUnavailableError(JobQueueError):
    """Raised when the queue is unavailable."""
    pass


class JobQueue:
    """
    Redis-backed job queue for distributed job processing.
    
    Uses Redis LIST data structure for reliable queue semantics:
    - RPUSH: Add job to queue (tail)
    - BRPOP: Block and pop job from queue (tail -> FIFO with LPUSH)
    - LPUSH + BRPOP: FIFO queue
    
    Message format:
    {
        "job_id": int,
        "enqueued_at": ISO timestamp,
        "priority": int (optional, for future use)
    }
    """
    
    def __init__(
        self,
        queue_name: Optional[str] = None,
        redis_client: Optional[RedisClient] = None
    ):
        """
        Initialize job queue.
        
        Args:
            queue_name: Optional queue name (uses config default if not provided)
            redis_client: Optional Redis client (uses singleton if not provided)
        """
        self.queue_name = queue_name or settings.job_queue_name
        self.redis = redis_client or get_redis_client()
        
        # Processing queue for reliability (jobs being processed)
        self.processing_queue = f"{self.queue_name}:processing"
    
    @property
    def is_available(self) -> bool:
        """Check if queue is available."""
        return self.redis.is_available
    
    def enqueue(self, job_id: int, priority: int = 0) -> bool:
        """
        Add a job to the queue.
        
        Args:
            job_id: Job ID to enqueue
            priority: Job priority (reserved for future use)
            
        Returns:
            True if successfully enqueued
            
        Raises:
            QueueUnavailableError: If Redis is unavailable
        """
        if not self.is_available:
            logger.error("Cannot enqueue job - queue unavailable")
            raise QueueUnavailableError("Job queue is unavailable")
        
        message = {
            "job_id": job_id,
            "enqueued_at": datetime.now(timezone.utc).isoformat(),
            "priority": priority,
        }
        
        # LPUSH for FIFO with BRPOP
        result = self.redis.lpush(self.queue_name, json.dumps(message))
        
        if result is not None:
            logger.info(f"Job enqueued: job_id={job_id}, queue_length={result}")
            return True
        
        logger.error(f"Failed to enqueue job: job_id={job_id}")
        return False
    
    def dequeue(self, timeout: int = 0) -> Optional[dict]:
        """
        Remove and return a job from the queue.
        
        Uses blocking pop for efficient polling.
        
        Args:
            timeout: Seconds to wait for job (0 = block forever)
            
        Returns:
            Job message dict or None if timeout/unavailable
        """
        if not self.is_available:
            logger.debug("Queue unavailable for dequeue")
            return None
        
        # BRPOP blocks until item available or timeout
        result = self.redis.brpop([self.queue_name], timeout=timeout)
        
        if result is None:
            return None
        
        try:
            # result is (queue_name, value)
            queue_name, message_str = result
            message = json.loads(message_str)
            
            logger.info(f"Job dequeued: job_id={message.get('job_id')}")
            return message
            
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse queue message: {e}")
            return None
    
    def dequeue_nonblocking(self) -> Optional[dict]:
        """
        Non-blocking dequeue.
        
        Returns:
            Job message dict or None if queue empty
        """
        if not self.is_available:
            return None
        
        message_str = self.redis.rpop(self.queue_name)
        
        if message_str is None:
            return None
        
        try:
            message = json.loads(message_str)
            logger.info(f"Job dequeued (non-blocking): job_id={message.get('job_id')}")
            return message
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse queue message: {e}")
            return None
    
    def peek(self) -> Optional[dict]:
        """
        View next job without removing it.
        
        Returns:
            Job message dict or None if queue empty
        """
        if not self.is_available:
            return None
        
        # LRANGE to get last element (BRPOP pops from right)
        messages = self.redis.lrange(self.queue_name, -1, -1)
        
        if not messages:
            return None
        
        try:
            return json.loads(messages[0])
        except (json.JSONDecodeError, TypeError):
            return None
    
    def size(self) -> int:
        """
        Get current queue size.
        
        Returns:
            Number of jobs in queue
        """
        return self.redis.llen(self.queue_name)
    
    def clear(self) -> int:
        """
        Clear all jobs from the queue.
        
        Use with caution! Primarily for testing.
        
        Returns:
            Number of jobs cleared
        """
        if not self.is_available:
            return 0
        
        count = self.size()
        self.redis.delete(self.queue_name)
        
        logger.warning(f"Queue cleared: {count} jobs removed")
        return count
    
    def requeue(self, job_id: int) -> bool:
        """
        Re-add a failed job to the queue.
        
        Used when job processing fails and needs retry.
        
        Args:
            job_id: Job ID to requeue
            
        Returns:
            True if successfully requeued
        """
        return self.enqueue(job_id, priority=-1)  # Lower priority for retries
    
    def health_check(self) -> dict:
        """
        Check queue health.
        
        Returns:
            Dictionary with status info
        """
        available = self.is_available
        
        return {
            "available": available,
            "queue_name": self.queue_name,
            "size": self.size() if available else 0,
            "redis": self.redis.health_check() if self.redis else {"status": "not_initialized"}
        }


# =============================================================================
# Module-level singleton
# =============================================================================

_job_queue: Optional[JobQueue] = None


def get_job_queue() -> JobQueue:
    """
    Get JobQueue singleton instance.
    
    Returns:
        JobQueue instance
    """
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue()
    return _job_queue
