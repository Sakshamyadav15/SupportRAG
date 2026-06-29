"""
Job Processor Registry and Dispatcher

Provides a centralized registry of job processors and dispatcher logic.
Each job type maps to a specific processor class.
"""

from typing import Type, Dict, Any
from .support_rag_processor import SupportRAGProcessor


class ProcessorNotFoundError(Exception):
    """Raised when a processor for the job type is not found."""
    pass


class JobProcessorRegistry:
    """
    Registry for job processors.
    
    Maps job type strings to processor classes for dynamic dispatch.
    """
    
    # Registry mapping job type to processor class
    _processors: Dict[str, Type] = {
        "support_rag": SupportRAGProcessor,
    }
    
    @classmethod
    def register(cls, job_type: str, processor_class: Type) -> None:
        """
        Register a processor for a job type.
        
        Args:
            job_type: String identifier for the job type
            processor_class: Processor class with async process() method
        """
        cls._processors[job_type] = processor_class
    
    @classmethod
    def get_processor(cls, job_type: str) -> Type:
        """
        Get processor class for a job type.
        
        Args:
            job_type: String identifier for the job type
            
        Returns:
            Processor class
            
        Raises:
            ProcessorNotFoundError: If job type not registered
        """
        if job_type not in cls._processors:
            available = ", ".join(cls._processors.keys())
            raise ProcessorNotFoundError(
                f"No processor registered for job type '{job_type}'. "
                f"Available types: {available}"
            )
        return cls._processors[job_type]
    
    @classmethod
    def get_all_types(cls) -> list[str]:
        """
        Get all registered job types.
        
        Returns:
            List of job type strings
        """
        return list(cls._processors.keys())
    
    @classmethod
    async def process_job(cls, job: Any) -> dict[str, Any]:
        """
        Dispatch job to appropriate processor.
        
        Args:
            job: Job object with id, type, payload (dict), status
            
        Returns:
            Result dictionary from processor
        """
        try:
            job_type = getattr(job, "type", None)
            
            if not job_type:
                return {
                    "status": "failed",
                    "error": "Job type not specified",
                }
            
            processor_class = cls.get_processor(job_type)
            processor = processor_class()
            result = await processor.process(job)
            
            return result
            
        except ProcessorNotFoundError as e:
            return {
                "status": "failed",
                "error": str(e),
                "error_type": "ProcessorNotFoundError",
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
            }


# Export registry for easy access
__all__ = [
    "JobProcessorRegistry",
    "ProcessorNotFoundError",
    "SupportRAGProcessor",
]
