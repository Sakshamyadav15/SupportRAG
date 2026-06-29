"""
Worker Configuration Module

Handles all worker settings using Pydantic Settings.
Separate from API config to allow independent deployment.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """
    Worker service settings loaded from environment variables.
    """

    # Database
    database_url: str = "postgresql://postgres:password@127.0.0.1:5433/jobsystem"

    # Redis Settings
    redis_url: str = "redis://127.0.0.1:6380/0"
    redis_max_connections: int = 10
    redis_socket_timeout: float = 5.0

    # Queue Settings
    job_queue_name: str = "job_queue"
    queue_poll_timeout: int = 5  # Seconds to block-wait for a job

    # Worker Settings
    worker_id: str = "worker-1"
    max_retries: int = 3
    processing_timeout: int = 300  # 5 minutes max per job

    # Cache Settings (for post-job cache invalidation)
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300

    # ── SupportRAG / Groq Settings ──────────────────────────────────────────
    # Groq API key (also read by SupportRAG's own settings.py via env)
    groq_api_key: str = ""

    # Groq rate limits (sliding-window, applied by GroqRateLimiter)
    # Free-tier defaults for llama-3.3-70b-versatile:
    #   30 requests / minute  |  6 000 tokens / minute
    groq_requests_per_minute: int = 30
    groq_tokens_per_minute: int = 6000

    # Vector Store Settings
    vector_store_path: str = "./data/vector_stores"
    # Set False on Windows if faiss IVF causes segfaults
    use_vector_store_ivf: bool = False

    # Application
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_worker_settings() -> WorkerSettings:
    """Returns cached worker settings instance."""
    return WorkerSettings()
