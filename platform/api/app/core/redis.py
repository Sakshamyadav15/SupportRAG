"""
Redis Client Module

Provides async-safe Redis client with singleton pattern.
Handles connection management and graceful degradation when Redis is unavailable.
"""

import redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
from typing import Optional, Any
from contextlib import contextmanager

from app.core.config import get_settings
from app.core.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()


class RedisClient:
    """
    Thread-safe Redis client wrapper with singleton pattern.
    
    Features:
    - Connection pooling
    - Automatic reconnection
    - Graceful degradation when Redis unavailable
    - Health check support
    """
    
    _instance: Optional["RedisClient"] = None
    _pool: Optional[redis.ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    _available: bool = False
    
    def __new__(cls) -> "RedisClient":
        """Singleton pattern - only one instance per process."""
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
                decode_responses=True,  # Return strings instead of bytes
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            self._client.ping()
            self._available = True
            logger.info("Redis connection established successfully")
            
        except (RedisError, RedisConnectionError) as e:
            logger.warning(f"Redis connection failed: {e}. Running in degraded mode.")
            self._available = False
            self._client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is currently available."""
        if not self._available or self._client is None:
            return False
        
        try:
            self._client.ping()
            return True
        except (RedisError, RedisConnectionError):
            self._available = False
            logger.warning("Redis became unavailable")
            return False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to Redis."""
        logger.info("Attempting Redis reconnection...")
        self._initialize()
        return self._available
    
    @contextmanager
    def safe_operation(self):
        """
        Context manager for safe Redis operations.
        
        Yields the client if available, None otherwise.
        Handles exceptions gracefully and logs warnings.
        
        Usage:
            with redis_client.safe_operation() as client:
                if client:
                    client.set("key", "value")
        """
        if not self.is_available:
            yield None
            return
        
        try:
            yield self._client
        except (RedisError, RedisConnectionError) as e:
            logger.warning(f"Redis operation failed: {e}")
            self._available = False
            yield None
    
    # ==========================================================================
    # Basic Operations with Graceful Degradation
    # ==========================================================================
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key. Returns None if Redis unavailable or key missing."""
        with self.safe_operation() as client:
            if client:
                return client.get(key)
        return None
    
    def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        Set key-value pair.
        
        Args:
            key: Key name
            value: Value to store
            ex: Expire time in seconds
            px: Expire time in milliseconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            True if successful, False otherwise
        """
        with self.safe_operation() as client:
            if client:
                result = client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
                return result is True
        return False
    
    def delete(self, *keys: str) -> int:
        """Delete keys. Returns number of keys deleted."""
        with self.safe_operation() as client:
            if client and keys:
                return client.delete(*keys)
        return 0
    
    def exists(self, *keys: str) -> int:
        """Check if keys exist. Returns count of existing keys."""
        with self.safe_operation() as client:
            if client and keys:
                return client.exists(*keys)
        return 0
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration. Returns True if successful."""
        with self.safe_operation() as client:
            if client:
                return client.expire(key, seconds)
        return False
    
    def ttl(self, key: str) -> int:
        """Get time-to-live for key. Returns -2 if key doesn't exist."""
        with self.safe_operation() as client:
            if client:
                return client.ttl(key)
        return -2
    
    # ==========================================================================
    # Atomic Operations for Rate Limiting
    # ==========================================================================
    
    def incr(self, key: str) -> Optional[int]:
        """Increment key atomically. Returns new value or None if unavailable."""
        with self.safe_operation() as client:
            if client:
                return client.incr(key)
        return None
    
    def incrby(self, key: str, amount: int) -> Optional[int]:
        """Increment key by amount. Returns new value or None."""
        with self.safe_operation() as client:
            if client:
                return client.incrby(key, amount)
        return None
    
    def decr(self, key: str) -> Optional[int]:
        """Decrement key atomically. Returns new value or None."""
        with self.safe_operation() as client:
            if client:
                return client.decr(key)
        return None
    
    # ==========================================================================
    # List Operations for Job Queue
    # ==========================================================================
    
    def lpush(self, key: str, *values: str) -> Optional[int]:
        """Push values to head of list. Returns list length or None."""
        with self.safe_operation() as client:
            if client and values:
                return client.lpush(key, *values)
        return None
    
    def rpush(self, key: str, *values: str) -> Optional[int]:
        """Push values to tail of list. Returns list length or None."""
        with self.safe_operation() as client:
            if client and values:
                return client.rpush(key, *values)
        return None
    
    def lpop(self, key: str) -> Optional[str]:
        """Pop value from head of list. Returns value or None."""
        with self.safe_operation() as client:
            if client:
                return client.lpop(key)
        return None
    
    def rpop(self, key: str) -> Optional[str]:
        """Pop value from tail of list. Returns value or None."""
        with self.safe_operation() as client:
            if client:
                return client.rpop(key)
        return None
    
    def brpop(self, keys: list[str], timeout: int = 0) -> Optional[tuple[str, str]]:
        """
        Blocking pop from tail of list.
        
        Args:
            keys: List of keys to pop from
            timeout: Timeout in seconds (0 = block forever)
            
        Returns:
            Tuple of (key, value) or None if timeout/unavailable
        """
        with self.safe_operation() as client:
            if client and keys:
                return client.brpop(keys, timeout=timeout)
        return None
    
    def llen(self, key: str) -> int:
        """Get list length. Returns 0 if unavailable or key missing."""
        with self.safe_operation() as client:
            if client:
                return client.llen(key)
        return 0
    
    def lrange(self, key: str, start: int, end: int) -> list[str]:
        """Get list elements in range. Returns empty list if unavailable."""
        with self.safe_operation() as client:
            if client:
                return client.lrange(key, start, end)
        return []
    
    # ==========================================================================
    # Pipeline Support
    # ==========================================================================
    
    def pipeline(self, transaction: bool = True):
        """
        Create a pipeline for batch operations.
        
        Returns pipeline object or None if Redis unavailable.
        """
        if self.is_available and self._client:
            return self._client.pipeline(transaction=transaction)
        return None
    
    # ==========================================================================
    # Health Check
    # ==========================================================================
    
    def health_check(self) -> dict[str, Any]:
        """
        Perform health check on Redis connection.
        
        Returns:
            Dictionary with health status and info
        """
        if not self.is_available:
            return {
                "status": "unavailable",
                "message": "Redis connection not available"
            }
        
        try:
            info = self._client.info("server")
            return {
                "status": "healthy",
                "version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds"),
            }
        except (RedisError, RedisConnectionError) as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def close(self) -> None:
        """Close Redis connection pool."""
        if self._pool:
            self._pool.disconnect()
            logger.info("Redis connection pool closed")


# =============================================================================
# Module-level singleton accessor
# =============================================================================

def get_redis_client() -> RedisClient:
    """
    Get the Redis client singleton instance.
    
    Returns:
        RedisClient instance
    """
    return RedisClient()
