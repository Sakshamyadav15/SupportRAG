"""
Rate Limiter Middleware

Token bucket rate limiting implemented via Redis.
Supports per-user and per-IP limiting with graceful degradation.
"""

import time
from typing import Optional, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.core.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()


class TokenBucket:
    """
    Token bucket implementation using Redis.
    
    The token bucket algorithm allows:
    - Burst capacity (bucket_size)
    - Sustained rate (refill_rate tokens per second)
    
    Each request consumes one token. If no tokens available, request is rejected.
    """
    
    def __init__(
        self,
        bucket_size: int,
        refill_rate: float,
        prefix: str = "rate_limit"
    ):
        """
        Initialize token bucket.
        
        Args:
            bucket_size: Maximum tokens (burst capacity)
            refill_rate: Tokens added per second
            prefix: Redis key prefix
        """
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate
        self.prefix = prefix
        self.redis = get_redis_client()
    
    def _get_keys(self, identifier: str) -> tuple[str, str]:
        """Get Redis keys for tokens and last_refill timestamp."""
        base_key = f"{self.prefix}:{identifier}"
        return f"{base_key}:tokens", f"{base_key}:last_refill"
    
    def consume(self, identifier: str, tokens: int = 1) -> tuple[bool, dict]:
        """
        Attempt to consume tokens from the bucket.
        
        Args:
            identifier: Unique identifier (user_id or IP)
            tokens: Number of tokens to consume
            
        Returns:
            Tuple of (allowed: bool, info: dict with remaining, reset_at)
        """
        if not self.redis.is_available:
            # Graceful degradation: allow all requests if Redis down
            logger.debug("Rate limiter bypassed - Redis unavailable")
            return True, {"remaining": -1, "reset_at": 0, "degraded": True}
        
        tokens_key, refill_key = self._get_keys(identifier)
        
        # Use pipeline for atomic operation
        pipe = self.redis.pipeline()
        if pipe is None:
            return True, {"remaining": -1, "reset_at": 0, "degraded": True}
        
        try:
            current_time = time.time()
            
            # Get current state
            pipe.get(tokens_key)
            pipe.get(refill_key)
            results = pipe.execute()
            
            current_tokens = float(results[0]) if results[0] else self.bucket_size
            last_refill = float(results[1]) if results[1] else current_time
            
            # Calculate token refill
            time_passed = current_time - last_refill
            tokens_to_add = time_passed * self.refill_rate
            current_tokens = min(self.bucket_size, current_tokens + tokens_to_add)
            
            # Check if we have enough tokens
            if current_tokens >= tokens:
                # Consume tokens
                new_tokens = current_tokens - tokens
                
                # Update Redis
                pipe = self.redis.pipeline()
                pipe.set(tokens_key, str(new_tokens), ex=3600)  # 1 hour TTL
                pipe.set(refill_key, str(current_time), ex=3600)
                pipe.execute()
                
                # Calculate reset time (when bucket will be full again)
                tokens_needed = self.bucket_size - new_tokens
                reset_seconds = tokens_needed / self.refill_rate if self.refill_rate > 0 else 0
                
                return True, {
                    "remaining": int(new_tokens),
                    "reset_at": int(current_time + reset_seconds),
                    "limit": self.bucket_size,
                }
            else:
                # Not enough tokens - rate limited
                tokens_needed = tokens - current_tokens
                retry_after = tokens_needed / self.refill_rate if self.refill_rate > 0 else 60
                
                return False, {
                    "remaining": 0,
                    "reset_at": int(current_time + retry_after),
                    "retry_after": int(retry_after) + 1,
                    "limit": self.bucket_size,
                }
                
        except Exception as e:
            logger.warning(f"Rate limiter error: {e}")
            # Graceful degradation on error
            return True, {"remaining": -1, "reset_at": 0, "degraded": True}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    Applies token bucket rate limiting based on:
    - User ID (from JWT, for authenticated requests)
    - IP address (for unauthenticated requests)
    
    Gracefully degrades if Redis is unavailable.
    """
    
    # Paths to exclude from rate limiting
    EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/"}
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        
        # Calculate refill rate: tokens per second
        # requests_per_minute / 60 = requests per second
        refill_rate = settings.rate_limit_requests_per_minute / 60.0
        
        self.bucket = TokenBucket(
            bucket_size=settings.rate_limit_burst_size,
            refill_rate=refill_rate,
            prefix="rate_limit"
        )
        
        logger.info(
            f"Rate limiter initialized: {settings.rate_limit_requests_per_minute}/min, "
            f"burst={settings.rate_limit_burst_size}"
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiter."""
        
        # Check if rate limiting is enabled
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Determine rate limit identifier
        identifier = self._get_identifier(request)
        
        # Check rate limit
        allowed, info = self.bucket.consume(identifier)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for: {identifier}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": info.get("retry_after", 60),
                },
                headers={
                    "X-RateLimit-Limit": str(info.get("limit", 0)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info.get("reset_at", 0)),
                    "Retry-After": str(info.get("retry_after", 60)),
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        if not info.get("degraded"):
            response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(info.get("reset_at", 0))
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier from request.
        
        Uses user ID if authenticated (from JWT in Authorization header),
        otherwise falls back to client IP.
        """
        # Try to get user from JWT token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Import here to avoid circular imports
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                return f"user:{payload['sub']}"
        
        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.
        
        Handles X-Forwarded-For for reverse proxy setups.
        """
        # Check X-Forwarded-For header (from Nginx/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
