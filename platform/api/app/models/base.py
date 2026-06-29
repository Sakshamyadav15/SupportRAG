"""
Base Model Module

Provides the declarative base class for all SQLAlchemy models.
All models should inherit from Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    All model classes should inherit from this class.
    This enables SQLAlchemy to track all models for migrations
    and table creation.
    """
    pass
