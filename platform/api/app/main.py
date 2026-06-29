"""
FastAPI Application Entry Point

This is the main application module that creates and configures the FastAPI app.
Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import engine
from app.core.logging import setup_logging, get_logger
from app.core.redis import get_redis_client
from app.models.base import Base
from app.api.router import api_router
from app.middleware.rate_limiter import RateLimitMiddleware


# Initialize settings and logging
settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Creates database tables, initializes Redis
    - Shutdown: Cleanup tasks
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create database tables
    # In production, use Alembic migrations instead
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Initialize Redis connection
    redis_client = get_redis_client()
    if redis_client.is_available:
        logger.info("Redis connection established")
    else:
        logger.warning("Redis unavailable - running in degraded mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close Redis connection
    redis_client = get_redis_client()
    redis_client.close()
    logger.info("Redis connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Job Processing API - Phase 2 & 3
    
    A scalable backend platform for managing and processing jobs.
    
    ### Features
    - User registration and JWT authentication
    - Job creation and async processing
    - Ownership-based access control
    - Redis-backed rate limiting
    - Distributed job queue
    
    ### Authentication
    Protected endpoints require a JWT token in the Authorization header:
    ```
    Authorization: Bearer <your_token>
    ```
    
    Get a token by calling POST /auth/login with valid credentials.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# =============================================================================
# Middleware Stack (order matters - first added = outermost)
# =============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (Phase 2)
# Applied after CORS, before request processing
app.add_middleware(RateLimitMiddleware)


# Include API routes
app.include_router(api_router)


# Root endpoint redirect to docs
@app.get("/", include_in_schema=False)
def root():
    """Redirect root to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
