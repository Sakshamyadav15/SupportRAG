"""
Dependencies Module

FastAPI dependencies for dependency injection.
Provides database sessions, current user, and service instances.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.redis import get_redis_client, RedisClient
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.job_repository import JobRepository
from app.services.auth_service import AuthService
from app.services.job_service import JobService
from app.services.cache_service import CacheService, get_cache_service
from app.queue.job_queue import JobQueue, get_job_queue


# OAuth2 scheme for JWT token extraction from Authorization header
# tokenUrl points to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =============================================================================
# Database Dependency
# =============================================================================

# Type alias for database session dependency
DBSession = Annotated[Session, Depends(get_db)]


# =============================================================================
# Repository Dependencies
# =============================================================================

def get_user_repository(db: DBSession) -> UserRepository:
    """
    Dependency that provides UserRepository instance.
    
    Args:
        db: Database session from get_db
        
    Returns:
        UserRepository instance
    """
    return UserRepository(db)


def get_job_repository(db: DBSession) -> JobRepository:
    """
    Dependency that provides JobRepository instance.
    
    Args:
        db: Database session from get_db
        
    Returns:
        JobRepository instance
    """
    return JobRepository(db)


# Type aliases for repository dependencies
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
JobRepo = Annotated[JobRepository, Depends(get_job_repository)]


# =============================================================================
# Redis & Cache Dependencies
# =============================================================================

def get_redis() -> RedisClient:
    """
    Dependency that provides Redis client instance.
    
    Returns:
        RedisClient singleton instance
    """
    return get_redis_client()


def get_cache() -> CacheService:
    """
    Dependency that provides CacheService instance.
    
    Returns:
        CacheService instance
    """
    return get_cache_service()


def get_queue() -> JobQueue:
    """
    Dependency that provides JobQueue instance.
    
    Returns:
        JobQueue singleton instance
    """
    return get_job_queue()


# Type aliases for Redis/Cache dependencies
Redis = Annotated[RedisClient, Depends(get_redis)]
Cache = Annotated[CacheService, Depends(get_cache)]
Queue = Annotated[JobQueue, Depends(get_queue)]


# =============================================================================
# Service Dependencies
# =============================================================================

def get_auth_service(user_repo: UserRepo) -> AuthService:
    """
    Dependency that provides AuthService instance.
    
    Args:
        user_repo: UserRepository from dependency
        
    Returns:
        AuthService instance
    """
    return AuthService(user_repo)


def get_job_service(
    job_repo: JobRepo,
    cache: Cache,
    queue: Queue
) -> JobService:
    """
    Dependency that provides JobService instance.
    
    Args:
        job_repo: JobRepository from dependency
        cache: CacheService from dependency
        queue: JobQueue from dependency
        
    Returns:
        JobService instance
    """
    return JobService(job_repo, cache, queue)


# Type aliases for service dependencies
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
JobSvc = Annotated[JobService, Depends(get_job_service)]


# =============================================================================
# Authentication Dependencies
# =============================================================================

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: UserRepo
) -> User:
    """
    Dependency that extracts and validates current user from JWT token.
    
    This is used to protect routes - any route that includes this dependency
    will require valid JWT authentication.
    
    Args:
        token: JWT token from Authorization header
        user_repo: UserRepository for looking up user
        
    Returns:
        User instance for the authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extract user ID from 'sub' claim
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    # Convert to int and lookup user
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception
    
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_user)]
