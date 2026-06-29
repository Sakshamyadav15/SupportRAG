"""
Jobs Module

Provides job processors and registry for distributed job processing.
"""

from app.jobs.job_processor import JobProcessor, JobProcessorError
from app.jobs.processor import JobProcessorRegistry, ProcessorNotFoundError
from app.jobs.support_rag_processor import SupportRAGProcessor


__all__ = [
    # Legacy base processor
    "JobProcessor",
    "JobProcessorError",
    # New registry system
    "JobProcessorRegistry",
    "ProcessorNotFoundError",
    # Active processors
    "SupportRAGProcessor",
]
