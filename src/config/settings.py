"""
Configuration settings for SupportRAG application.
Loads environment variables and provides centralized config management.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    environment: str = "development"
    
    # API Keys
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_provider: str = "gemini"  # gemini or openai
    llm_model: str = "gemini-pro"
    llm_temperature: float = 0.7
    max_tokens: int = 512
    
    # Vector Database
    vector_db_path: str = "data/vector_store"
    vector_db_type: str = "faiss"
    index_name: str = "faq_index"
    
    # RAG Configuration
    top_k_results: int = 3
    confidence_threshold: float = 0.7
    max_context_length: int = 2048
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    metrics_file: str = "logs/metrics.json"
    
    # Data Paths
    faq_data_path: str = "data/faqs.csv"
    test_data_path: str = "data/test_queries.csv"
    
    # Performance
    batch_size: int = 32
    cache_ttl: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_vector_db_full_path(self) -> Path:
        """Get the full path to the vector database."""
        return Path(self.vector_db_path)
    
    def get_log_file_path(self) -> Path:
        """Get the full path to the log file."""
        return Path(self.log_file)
    
    def get_metrics_file_path(self) -> Path:
        """Get the full path to the metrics file."""
        return Path(self.metrics_file)
    
    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present."""
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            return False
        if self.llm_provider == "openai" and not self.openai_api_key:
            return False
        return True


# Global settings instance
settings = Settings()
