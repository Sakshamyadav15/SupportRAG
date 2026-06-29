"""
API Router

Aggregates all route modules into a single router.
This is the main entry point for API routes.
"""

from fastapi import APIRouter

from app.api.routes import auth, jobs, health


# Create main API router
api_router = APIRouter()

# Include all route modules
# Order matters for documentation - routes are displayed in this order
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(jobs.router)
