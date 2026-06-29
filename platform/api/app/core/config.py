"""
Core Configuration Module

Handles all application settings using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        database_url: PostgreSQL connection string
        secret_key: JWT signing secret (MUST be changed in production)
        algorithm: JWT signing algorithm
        access_token_expire_minutes: JWT token expiration time
        debug: Enable debug mode
        app_name: Application name for docs
        app_version: Application version
        redis_url: Redis connection string
        rate_limit_*: Rate limiting configuration
    """
    
    # Database
    database_url: str = "postgresql://postgres:password@127.0.0.1:5433/jobsystem"
    
    # Redis Settings (Phase 2)
    redis_url: str = "redis://127.0.0.1:6380/0"
    redis_max_connections: int = 10
    redis_socket_timeout: float = 5.0
    
    # Rate Limiting Settings (Phase 2)
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10
    
    # Cache Settings (Phase 2)
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes default
    
    # Queue Settings (Phase 3)
    job_queue_name: str = "job_queue"
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = False
    app_name: str = "Job Processing API"
    app_version: str = "2.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()
