"""
Worker Redis Client

Redis client for the worker service.
Reuses the same patterns as the API service.
"""

import redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
from typing import Optional, Any
from contextlib import contextmanager
import json

from app.core.config import get_worker_settings


settings = get_worker_settings()


class WorkerRedisClient:
    """
    Redis client for worker service.
    
    Provides queue operations and cache invalidation.
    """
    
    _instance: Optional["WorkerRedisClient"] = None
    _pool: Optional[redis.ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    _available: bool = False
    
    def __new__(cls) -> "WorkerRedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize Redis connection pool."""
        try:
            self._pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_timeout,
                decode_responses=True,
            )
            self._client = redis.Redis(connection_pool=self._pool)
            self._client.ping()
            self._available = True
            
        except (RedisError, RedisConnectionError) as e:
            print(f"Redis connection failed: {e}")
            self._available = False
            self._client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self._client is None:
            return False
        try:
            self._client.ping()
            self._available = True
            return True
        except (RedisError, RedisConnectionError):
            self._available = False
            return False
    
    @contextmanager
    def safe_operation(self):
        """Context manager for safe Redis operations."""
        if not self.is_available:
            yield None
            return
        try:
            yield self._client
        except (RedisError, RedisConnectionError):
            self._available = False
            # We do NOT yield None here. A context manager can only yield once.
            pass
    
    # Queue operations
    def brpop(self, keys: list[str], timeout: int = 0) -> Optional[tuple[str, str]]:
        """Blocking pop from queue."""
        with self.safe_operation() as client:
            if client and keys:
                return client.brpop(keys, timeout=timeout)
        return None
    
    def lpush(self, key: str, *values: str) -> Optional[int]:
        """Push to queue head."""
        with self.safe_operation() as client:
            if client and values:
                return client.lpush(key, *values)
        return None
    
    # Cache operations
    def delete(self, *keys: str) -> int:
        """Delete cache keys."""
        with self.safe_operation() as client:
            if client and keys:
                return client.delete(*keys)
        return 0
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set cache value."""
        with self.safe_operation() as client:
            if client:
                return client.set(key, value, ex=ex) is True
        return False
    
    def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            self._pool.disconnect()


def get_worker_redis() -> WorkerRedisClient:
    """Get Redis client singleton."""
    return WorkerRedisClient()
