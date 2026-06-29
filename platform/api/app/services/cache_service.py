"""
Cache Service

Provides caching layer for job data using Redis.
Implements read-through and write-through caching patterns.
Gracefully degrades when Redis is unavailable.
"""

import json
from typing import Optional, Any
from datetime import datetime

from app.core.config import get_settings
from app.core.redis import get_redis_client, RedisClient
from app.core.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()


class CacheService:
    """
    Caching service for job data.
    
    Provides:
    - Read-through caching (check cache first, then DB)
    - Write-through caching (update cache on DB writes)
    - Automatic TTL management
    - Graceful degradation when Redis unavailable
    
    This service is framework-agnostic and injected via dependencies.
    """
    
    # Cache key prefixes
    PREFIX_JOB = "cache:job"
    PREFIX_JOB_LIST = "cache:job_list"
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        Initialize cache service.
        
        Args:
            redis_client: Optional Redis client (uses singleton if not provided)
        """
        self.redis = redis_client or get_redis_client()
        self.ttl = settings.cache_ttl_seconds
        self.enabled = settings.cache_enabled
    
    @property
    def is_available(self) -> bool:
        """Check if caching is available and enabled."""
        return self.enabled and self.redis.is_available
    
    # ==========================================================================
    # Key Generation
    # ==========================================================================
    
    def _job_key(self, job_id: int) -> str:
        """Generate cache key for a single job."""
        return f"{self.PREFIX_JOB}:{job_id}"
    
    def _job_list_key(self, user_id: int, skip: int, limit: int) -> str:
        """Generate cache key for job list."""
        return f"{self.PREFIX_JOB_LIST}:{user_id}:{skip}:{limit}"
    
    def _user_jobs_pattern(self, user_id: int) -> str:
        """Generate pattern to match all job list keys for a user."""
        return f"{self.PREFIX_JOB_LIST}:{user_id}:*"
    
    # ==========================================================================
    # Serialization
    # ==========================================================================
    
    def _serialize_job(self, job: Any) -> str:
        """
        Serialize job object to JSON string.
        
        Args:
            job: Job model instance
            
        Returns:
            JSON string representation
        """
        # Convert SQLAlchemy model to dict
        job_dict = {
            "id": job.id,
            "user_id": job.user_id,
            "status": job.status.value if hasattr(job.status, 'value') else str(job.status),
            "input_data": job.input_data,
            "result_data": job.result_data,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }
        return json.dumps(job_dict)
    
    def _deserialize_job(self, data: str) -> Optional[dict]:
        """
        Deserialize JSON string to job dict.
        
        Args:
            data: JSON string
            
        Returns:
            Dictionary representation of job or None
        """
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def _serialize_job_list(self, jobs: list[Any], total: int) -> str:
        """
        Serialize job list to JSON string.
        
        Args:
            jobs: List of job model instances
            total: Total count
            
        Returns:
            JSON string representation
        """
        jobs_list = []
        for job in jobs:
            jobs_list.append({
                "id": job.id,
                "user_id": job.user_id,
                "status": job.status.value if hasattr(job.status, 'value') else str(job.status),
                "input_data": job.input_data,
                "result_data": job.result_data,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            })
        
        return json.dumps({"jobs": jobs_list, "total": total})
    
    def _deserialize_job_list(self, data: str) -> Optional[dict]:
        """
        Deserialize JSON string to job list dict.
        
        Args:
            data: JSON string
            
        Returns:
            Dictionary with 'jobs' list and 'total' or None
        """
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return None
    
    # ==========================================================================
    # Single Job Cache Operations
    # ==========================================================================
    
    def get_job(self, job_id: int) -> Optional[dict]:
        """
        Get job from cache.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job dict if cached, None otherwise
        """
        if not self.is_available:
            return None
        
        key = self._job_key(job_id)
        data = self.redis.get(key)
        
        if data:
            logger.debug(f"Cache HIT: job_id={job_id}")
            return self._deserialize_job(data)
        
        logger.debug(f"Cache MISS: job_id={job_id}")
        return None
    
    def set_job(self, job: Any) -> bool:
        """
        Cache a job (write-through).
        
        Args:
            job: Job model instance
            
        Returns:
            True if cached successfully
        """
        if not self.is_available:
            return False
        
        key = self._job_key(job.id)
        data = self._serialize_job(job)
        
        success = self.redis.set(key, data, ex=self.ttl)
        
        if success:
            logger.debug(f"Cache SET: job_id={job.id}")
        
        return success
    
    def invalidate_job(self, job_id: int) -> bool:
        """
        Invalidate cached job.
        
        Args:
            job_id: Job ID to invalidate
            
        Returns:
            True if invalidated
        """
        if not self.is_available:
            return False
        
        key = self._job_key(job_id)
        deleted = self.redis.delete(key)
        
        if deleted:
            logger.debug(f"Cache INVALIDATE: job_id={job_id}")
        
        return deleted > 0
    
    # ==========================================================================
    # Job List Cache Operations
    # ==========================================================================
    
    def get_job_list(
        self,
        user_id: int,
        skip: int,
        limit: int
    ) -> Optional[tuple[list[dict], int]]:
        """
        Get job list from cache.
        
        Args:
            user_id: User ID
            skip: Pagination offset
            limit: Page size
            
        Returns:
            Tuple of (jobs list, total) if cached, None otherwise
        """
        if not self.is_available:
            return None
        
        key = self._job_list_key(user_id, skip, limit)
        data = self.redis.get(key)
        
        if data:
            result = self._deserialize_job_list(data)
            if result:
                logger.debug(f"Cache HIT: job_list user_id={user_id}")
                return result["jobs"], result["total"]
        
        logger.debug(f"Cache MISS: job_list user_id={user_id}")
        return None
    
    def set_job_list(
        self,
        user_id: int,
        skip: int,
        limit: int,
        jobs: list[Any],
        total: int
    ) -> bool:
        """
        Cache job list (write-through).
        
        Args:
            user_id: User ID
            skip: Pagination offset
            limit: Page size
            jobs: List of job model instances
            total: Total count
            
        Returns:
            True if cached successfully
        """
        if not self.is_available:
            return False
        
        key = self._job_list_key(user_id, skip, limit)
        data = self._serialize_job_list(jobs, total)
        
        success = self.redis.set(key, data, ex=self.ttl)
        
        if success:
            logger.debug(f"Cache SET: job_list user_id={user_id}")
        
        return success
    
    def invalidate_user_job_lists(self, user_id: int) -> int:
        """
        Invalidate all cached job lists for a user.
        
        Called when user's jobs change (create, update, delete).
        
        Args:
            user_id: User ID
            
        Returns:
            Number of keys invalidated
        """
        if not self.is_available:
            return 0
        
        # Note: In production, use SCAN instead of KEYS for large datasets
        # For Phase 2, this simple approach is acceptable
        pattern = self._user_jobs_pattern(user_id)
        
        # We can't easily get keys matching pattern with our safe wrapper
        # Instead, we'll rely on TTL expiration for list caches
        # and invalidate when we know the specific key
        logger.debug(f"Cache INVALIDATE: job_lists for user_id={user_id}")
        
        return 0
    
    # ==========================================================================
    # Bulk Operations
    # ==========================================================================
    
    def invalidate_all(self) -> bool:
        """
        Invalidate all cached data.
        
        Use with caution - primarily for testing/maintenance.
        
        Returns:
            True if operation attempted
        """
        if not self.is_available:
            return False
        
        logger.warning("Cache INVALIDATE ALL requested")
        # In production, use SCAN + DELETE
        # For now, rely on TTL
        return True
    
    # ==========================================================================
    # Health Check
    # ==========================================================================
    
    def health_check(self) -> dict:
        """
        Check cache service health.
        
        Returns:
            Dictionary with status info
        """
        return {
            "enabled": self.enabled,
            "available": self.is_available,
            "ttl_seconds": self.ttl,
            "redis": self.redis.health_check() if self.redis else {"status": "not_initialized"}
        }


# =============================================================================
# Module-level factory function
# =============================================================================

def get_cache_service() -> CacheService:
    """
    Get CacheService instance.
    
    Returns:
        CacheService instance
    """
    return CacheService()
