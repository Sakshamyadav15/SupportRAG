"""
Jobs Routes

API endpoints for job operations (create, get, list).
This layer handles HTTP parsing, validation, and response formatting.
Business logic is delegated to JobService.
All routes are protected and require JWT authentication.
"""

from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.job import (
    JobCreateRequest,
    JobResponse,
    JobListResponse,
)
from app.services.job_service import JobNotFoundError
from app.dependencies import JobSvc, CurrentUser


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
    description="Create a new processing job. Requires authentication."
)
def create_job(
    request: JobCreateRequest,
    job_service: JobSvc,
    current_user: CurrentUser
) -> JobResponse:
    """
    Create a new job for the authenticated user.
    
    - **input_data**: JSON object containing job input parameters
    
    The job will be processed synchronously in Phase 1.
    In future phases, jobs will be queued for async processing.
    """
    job = job_service.create_job(
        user_id=current_user.id,
        input_data=request.input_data
    )
    
    return JobResponse.model_validate(job)


@router.get(
    "",
    response_model=JobListResponse,
    summary="List my jobs",
    description="Get list of jobs for the authenticated user."
)
def list_jobs(
    job_service: JobSvc,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=100, description="Max records to return")
) -> JobListResponse:
    """
    List all jobs belonging to the authenticated user.
    
    - **skip**: Pagination offset (default: 0)
    - **limit**: Maximum number of results (default: 100, max: 100)
    
    Users can only see their own jobs.
    """
    jobs, total = job_service.list_user_jobs(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return JobListResponse(
        jobs=[JobResponse.model_validate(job) for job in jobs],
        total=total
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job by ID",
    description="Get details of a specific job. Users can only access their own jobs."
)
def get_job(
    job_id: int,
    job_service: JobSvc,
    current_user: CurrentUser
) -> JobResponse:
    """
    Get a specific job by ID.
    
    - **job_id**: The job's unique identifier
    
    Returns 404 if job doesn't exist or doesn't belong to the authenticated user.
    """
    try:
        job = job_service.get_job(
            job_id=job_id,
            user_id=current_user.id
        )
        
        return JobResponse.model_validate(job)
        
    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id={job_id} not found"
        )
