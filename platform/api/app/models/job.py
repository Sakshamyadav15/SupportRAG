"""
Job Model

SQLAlchemy ORM model for the Job entity.
Represents processing jobs created by users.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class JobStatus(str, enum.Enum):
    """
    Enumeration of possible job statuses.
    
    Inheriting from str makes it JSON serializable.
    """
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(Base):
    """
    Job entity representing a processing task.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to the owning user
        status: Current job status
        input_data: JSON/text input for processing
        result_data: Processing result (nullable)
        created_at: Timestamp when job was created
        updated_at: Timestamp when job was last modified
        user: Relationship to the owning user
    """
    
    __tablename__ = "jobs"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Foreign key to users table
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index for fast user job lookups
    )
    
    # Job status with enum constraint
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False
    )
    
    # Job type - determines which processor handles this job
    type: Mapped[str] = mapped_column(
        String(50),
        default="support_rag",
        nullable=False,
        index=True  # Index for job type queries
    )
    
    # Input data - stored as JSON string or text
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Result data - nullable until job completes
    result_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationship to user - many jobs belong to one user
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    
    def __repr__(self) -> str:
        return f"<Job(id={self.id}, status={self.status}, user_id={self.user_id})>"


# Import User here to avoid circular imports
from app.models.user import User
