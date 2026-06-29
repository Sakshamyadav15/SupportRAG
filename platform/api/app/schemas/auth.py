"""
Auth Schemas

Pydantic schemas for authentication-related requests and responses.
These are DTOs (Data Transfer Objects) for the API layer.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Request schema for user registration.
    
    Validates email format and password requirements.
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters)",
        examples=["securepassword123"]
    )


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="User's password",
        examples=["securepassword123"]
    )


class TokenResponse(BaseModel):
    """
    Response schema for successful authentication.
    
    Returns JWT access token and token type.
    """
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )


class RegisterResponse(BaseModel):
    """
    Response schema for successful registration.
    """
    id: int = Field(..., description="Created user's ID")
    email: str = Field(..., description="Created user's email")
    message: str = Field(
        default="User registered successfully",
        description="Success message"
    )
