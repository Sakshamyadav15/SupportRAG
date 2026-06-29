"""
Schemas Module

Exports all Pydantic schemas (DTOs) for the API.
"""

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RegisterResponse,
)
from app.schemas.user import (
    UserBase,
    UserResponse,
    UserInDB,
)
from app.schemas.job import (
    JobCreateRequest,
    JobResponse,
    JobListResponse,
)


__all__ = [
    # Auth schemas
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RegisterResponse",
    # User schemas
    "UserBase",
    "UserResponse",
    "UserInDB",
    # Job schemas
    "JobCreateRequest",
    "JobResponse",
    "JobListResponse",
]
