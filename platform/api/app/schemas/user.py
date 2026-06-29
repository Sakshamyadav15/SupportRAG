"""
User Schemas

Pydantic schemas for user-related data transfer.
Used for representing user data in API responses.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    """
    email: EmailStr = Field(..., description="User's email address")


class UserResponse(UserBase):
    """
    Response schema for user data.
    
    Excludes sensitive fields like password_hash.
    """
    id: int = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = {
        "from_attributes": True  # Enables ORM mode for SQLAlchemy models
    }


class UserInDB(UserBase):
    """
    Internal schema representing user as stored in database.
    
    Used internally, never exposed to API responses.
    """
    id: int
    password_hash: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }
