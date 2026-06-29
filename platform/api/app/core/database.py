"""
Database Configuration Module

Sets up SQLAlchemy engine, session factory, and provides
a dependency for getting database sessions in routes.
"""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings


# Get settings
settings = get_settings()

# Create SQLAlchemy engine
# pool_pre_ping ensures connections are valid before use
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Session factory - creates new sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields a session and ensures it's closed after the request.
    This is used as a FastAPI dependency in routes.
    
    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
