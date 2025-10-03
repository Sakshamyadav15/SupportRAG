"""
Logging utility for SupportRAG application.
Provides consistent logging across all modules.
"""
import logging
import sys
from pathlib import Path
from loguru import logger as loguru_logger
from src.config import settings


def setup_logging():
    """Configure application-wide logging."""
    # Remove default handler
    loguru_logger.remove()
    
    # Console handler
    loguru_logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # File handler
    log_path = settings.get_log_file_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    loguru_logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip"
    )


def get_logger(name: str):
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return loguru_logger.bind(name=name)


# Setup logging on import
setup_logging()
