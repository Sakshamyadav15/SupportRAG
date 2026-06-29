"""
Health Routes

API endpoints for system health checks.
These endpoints are public (no authentication required).
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import get_settings


router = APIRouter(tags=["System"])


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Current server timestamp")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API service is running and healthy."
)
def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns basic information about the service status.
    This endpoint is public and doesn't require authentication.
    
    Used by:
    - Load balancers for health monitoring
    - Kubernetes liveness/readiness probes
    - Monitoring systems
    """
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc)
    )
