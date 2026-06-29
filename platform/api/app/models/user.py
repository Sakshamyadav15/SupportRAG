"""
User Model

SQLAlchemy ORM model for the User entity.
Represents users who can authenticate and create jobs.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """
    User entity representing an authenticated user.
    
    Attributes:
        id: Primary key
        email: Unique email address (used for login)
        password_hash: Bcrypt hashed password
        created_at: Timestamp when user was created
        jobs: Relationship to user's jobs
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Email must be unique and indexed for fast lookups during login
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    
    # Hashed password - never store plain text!
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Automatic timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationship to jobs - one user has many jobs
    # back_populates creates bidirectional relationship
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


# Import Job here to avoid circular imports
# This is a forward reference pattern
from app.models.job import Job
