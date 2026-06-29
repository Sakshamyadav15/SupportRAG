"""
Core Module

Exports core utilities for the application.
"""

from app.core.config import Settings, get_settings
from app.core.database import get_db, engine, SessionLocal
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.logging import setup_logging, get_logger
from app.core.redis import RedisClient, get_redis_client


__all__ = [
    # Config
    "Settings",
    "get_settings",
    # Database
    "get_db",
    "engine",
    "SessionLocal",
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    # Logging
    "setup_logging",
    "get_logger",
    # Redis
    "RedisClient",
    "get_redis_client",
]
