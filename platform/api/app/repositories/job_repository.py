"""
Job Repository

Data access layer for Job entity.
Contains all database queries related to jobs.
This layer ONLY talks to SQLAlchemy, no business logic here.
"""

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.core.logging import get_logger


logger = get_logger(__name__)


class JobRepository:
    """
    Repository for Job database operations.
    
    All methods accept a Session and perform atomic operations.
    No business logic should be placed here.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy session instance
        """
        self.db = db
    
    def create(self, user_id: int, input_data: str, job_type: str = "support_rag") -> Job:
        """
        Create a new job in the database.
        
        Args:
            user_id: ID of the user creating the job
            input_data: JSON string of input data
            job_type: Type of job (determines which processor handles it)
            
        Returns:
            Created Job instance
        """
        job = Job(
            user_id=user_id,
            input_data=input_data,
            type=job_type,
            status=JobStatus.PENDING
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Created job with id={job.id} for user_id={user_id}, type={job_type}")
        return job
    
    def get_by_id(self, job_id: int) -> Job | None:
        """
        Retrieve a job by its ID.
        
        Args:
            job_id: Job's primary key
            
        Returns:
            Job if found, None otherwise
        """
        stmt = select(Job).where(Job.id == job_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by_id_and_user(self, job_id: int, user_id: int) -> Job | None:
        """
        Retrieve a job by ID only if owned by the specified user.
        
        This enforces ownership - users can only access their own jobs.
        
        Args:
            job_id: Job's primary key
            user_id: Expected owner's user ID
            
        Returns:
            Job if found and owned by user, None otherwise
        """
        stmt = select(Job).where(
            Job.id == job_id,
            Job.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_all_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Job]:
        """
        Retrieve all jobs for a specific user with pagination.
        
        Args:
            user_id: User's ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Job instances
        """
        stmt = (
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt).scalars().all()
        return list(result)
    
    def count_by_user(self, user_id: int) -> int:
        """
        Count total jobs for a specific user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Total number of jobs
        """
        from sqlalchemy import func
        stmt = select(func.count()).select_from(Job).where(Job.user_id == user_id)
        result = self.db.execute(stmt).scalar()
        return result or 0
    
    def update_status(
        self,
        job_id: int,
        status: JobStatus,
        result_data: str | None = None
    ) -> Job | None:
        """
        Update a job's status and optionally its result data.
        
        Args:
            job_id: Job's primary key
            status: New status to set
            result_data: Optional result data (for completed jobs)
            
        Returns:
            Updated Job if found, None otherwise
        """
        job = self.get_by_id(job_id)
        if job is None:
            return None
        
        job.status = status
        if result_data is not None:
            job.result_data = result_data
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Updated job id={job_id} status to {status}")
        return job
