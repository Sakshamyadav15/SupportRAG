"""
Job Service

Business logic for job operations.
This service orchestrates repositories and does NOT know about FastAPI.
"""

import json
from typing import Optional
from app.repositories.job_repository import JobRepository
from app.models.job import Job, JobStatus
from app.core.logging import get_logger
from app.queue.job_queue import get_job_queue, JobQueue, QueueUnavailableError
from app.services.cache_service import CacheService, get_cache_service


logger = get_logger(__name__)


class JobServiceError(Exception):
    """Base exception for job service errors."""
    pass


class JobNotFoundError(JobServiceError):
    """Raised when a job is not found or not accessible."""
    pass


class JobService:
    """
    Service layer for job operations.
    
    Contains business logic for:
    - Job creation
    - Job retrieval (with ownership check)
    - Job listing
    - Job queueing (Phase 3: async via Redis queue)
    
    This service is framework-agnostic and only uses repositories.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        cache_service: Optional[CacheService] = None,
        job_queue: Optional[JobQueue] = None
    ):
        """
        Initialize job service with required dependencies.
        
        Args:
            job_repository: Repository for job database operations
            cache_service: Optional cache service for read-through caching
            job_queue: Optional job queue for async processing
        """
        self.job_repository = job_repository
        self.cache_service = cache_service or get_cache_service()
        self.job_queue = job_queue or get_job_queue()
    
    def create_job(self, user_id: int, input_data: dict, job_type: str = "support_rag") -> Job:
        """
        Create a new job and queue it for async processing.
        
        Phase 3: Jobs are queued for worker processing.
        The API returns immediately with PENDING status.
        
        Args:
            user_id: ID of the user creating the job
            input_data: Dictionary of input data for processing
            job_type: Type of job (determines which processor handles it)
            
        Returns:
            Created Job instance (status=PENDING)
        """
        # Convert input data to JSON string for storage
        input_json = json.dumps(input_data)
        
        # Create the job via repository
        job = self.job_repository.create(
            user_id=user_id,
            input_data=input_json,
            job_type=job_type
        )
        
        logger.info(f"Job created: id={job.id}, user_id={user_id}, type={job_type}")
        
        # Queue job for async processing (Phase 3)
        try:
            self.job_queue.enqueue(job.id)
            logger.info(f"Job queued for processing: id={job.id}")
        except QueueUnavailableError:
            # If queue unavailable, mark job as failed
            logger.error(f"Failed to queue job: id={job.id} - queue unavailable")
            self.job_repository.update_status(
                job.id,
                JobStatus.FAILED,
                result_data=json.dumps({"error": "Queue unavailable"})
            )
            # Refresh job to get updated status
            job = self.job_repository.get_by_id(job.id)
        
        # Invalidate user's job list cache
        self.cache_service.invalidate_user_job_lists(user_id)
        
        return job
    
    def get_job(self, job_id: int, user_id: int) -> Job:
        """
        Retrieve a job by ID with ownership check.
        
        Uses read-through cache: check cache first, then DB.
        
        Business rule: Users can only access their own jobs.
        
        Args:
            job_id: Job's ID
            user_id: Requesting user's ID
            
        Returns:
            Job instance
            
        Raises:
            JobNotFoundError: If job not found or not owned by user
        """
        # Try cache first (read-through pattern)
        cached = self.cache_service.get_job(job_id)
        if cached and cached.get("user_id") == user_id:
            # Cache hit - but we need to verify ownership
            logger.debug(f"Cache hit for job_id={job_id}")
            # Still fetch from DB for fresh data and proper model
            # Cache is optimization, not source of truth
        
        # Fetch from database with ownership check
        job = self.job_repository.get_by_id_and_user(job_id, user_id)
        
        if job is None:
            logger.warning(f"Job access denied: job_id={job_id}, user_id={user_id}")
            raise JobNotFoundError(f"Job with id={job_id} not found")
        
        # Cache the job (write-through on read)
        self.cache_service.set_job(job)
        
        return job
    
    def list_user_jobs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Job], int]:
        """
        List all jobs for a user with pagination.
        
        Uses read-through cache for performance.
        
        Args:
            user_id: User's ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (list of jobs, total count)
        """
        # Note: List caching is tricky due to invalidation complexity
        # For Phase 2, we fetch from DB but cache individual jobs
        
        jobs = self.job_repository.get_all_by_user(user_id, skip, limit)
        total = self.job_repository.count_by_user(user_id)
        
        # Cache individual jobs for potential future get_job calls
        for job in jobs:
            self.cache_service.set_job(job)
        
        logger.debug(f"Listed {len(jobs)} jobs for user_id={user_id}")
        return jobs, total
    
    def update_job_status(
        self,
        job_id: int,
        status: JobStatus,
        result_data: Optional[str] = None
    ) -> Optional[Job]:
        """
        Update job status (used by worker service).
        
        This method is called by the worker after processing.
        Updates database and invalidates cache.
        
        Args:
            job_id: Job's ID
            status: New status
            result_data: Optional result data (for completed jobs)
            
        Returns:
            Updated Job or None if not found
        """
        job = self.job_repository.update_status(job_id, status, result_data)
        
        if job:
            # Invalidate cache for this job
            self.cache_service.invalidate_job(job_id)
            # Also invalidate user's job lists
            self.cache_service.invalidate_user_job_lists(job.user_id)
            logger.info(f"Job status updated: id={job_id}, status={status}")
        
        return job
    
    def get_job_for_processing(self, job_id: int) -> Optional[Job]:
        """
        Get job for worker processing (no ownership check).
        
        This is used by the worker service to fetch job details.
        Does NOT enforce ownership - workers process all jobs.
        
        Args:
            job_id: Job's ID
            
        Returns:
            Job or None if not found
        """
        return self.job_repository.get_by_id(job_id)
