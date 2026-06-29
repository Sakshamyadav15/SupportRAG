"""
Job Schemas

Pydantic schemas for job-related requests and responses.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.models.job import JobStatus


class JobCreateRequest(BaseModel):
    """
    Request schema for creating a new job.
    
    The input_data field accepts any JSON-serializable data.
    """
    input_data: dict[str, Any] = Field(
        ...,
        description="Input data for job processing",
        examples=[{"task": "process_data", "params": {"key": "value"}}]
    )


class JobResponse(BaseModel):
    """
    Response schema for job data.
    
    Represents a job as returned by the API.
    """
    id: int = Field(..., description="Job's unique identifier")
    user_id: int = Field(..., description="ID of the job owner")
    status: JobStatus = Field(..., description="Current job status")
    input_data: str = Field(..., description="Job input data as JSON string")
    result_data: str | None = Field(None, description="Job result data (if completed)")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True  # Enables ORM mode for SQLAlchemy models
    }


class JobListResponse(BaseModel):
    """
    Response schema for listing multiple jobs.
    """
    jobs: list[JobResponse] = Field(
        default_factory=list,
        description="List of jobs"
    )
    total: int = Field(..., description="Total number of jobs")
