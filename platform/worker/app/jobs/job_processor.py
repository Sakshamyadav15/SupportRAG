"""
Job Processor

Contains the actual job processing logic.
This is where business logic for processing jobs lives.
"""

import json
import time
import random
from typing import Any
from datetime import datetime, timezone

from app.core.config import get_worker_settings


settings = get_worker_settings()


class JobProcessorError(Exception):
    """Base exception for job processor errors."""
    pass


class JobProcessor:
    """
    Processes jobs fetched from the queue.
    
    This class contains the actual business logic for job processing.
    In a real system, this would contain domain-specific processing.
    """
    
    def __init__(self, worker_id: str):
        """
        Initialize processor.
        
        Args:
            worker_id: Unique identifier for this worker
        """
        self.worker_id = worker_id
    
    def process(self, job_id: int, input_data: str) -> dict[str, Any]:
        """
        Process a job and return the result.
        
        This is the main processing entry point.
        Simulates heavy computation for demonstration.
        
        Args:
            job_id: Job ID being processed
            input_data: JSON string of input data
            
        Returns:
            Dictionary containing processing result
            
        Raises:
            JobProcessorError: If processing fails
        """
        print(f"[{self.worker_id}] Processing job {job_id}...")
        
        try:
            # Parse input data
            input_dict = json.loads(input_data)
            
            # Simulate heavy processing
            processing_time = self._simulate_processing()
            
            # Generate result
            result = {
                "status": "completed",
                "processed_by": self.worker_id,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "processing_time_seconds": processing_time,
                "input_received": input_dict,
                "output": self._transform_data(input_dict),
            }
            
            print(f"[{self.worker_id}] Job {job_id} completed in {processing_time:.2f}s")
            return result
            
        except json.JSONDecodeError as e:
            raise JobProcessorError(f"Invalid input data format: {e}")
        except Exception as e:
            raise JobProcessorError(f"Processing failed: {e}")
    
    def _simulate_processing(self) -> float:
        """
        Simulate heavy processing work.
        
        In a real system, this would be actual computation.
        
        Returns:
            Processing time in seconds
        """
        # Random processing time between 1-5 seconds
        processing_time = random.uniform(1.0, 5.0)
        time.sleep(processing_time)
        return processing_time
    
    def _transform_data(self, input_data: dict) -> dict:
        """
        Transform input data into output.
        
        This is a placeholder for actual business logic.
        
        Args:
            input_data: Input dictionary
            
        Returns:
            Transformed output dictionary
        """
        # Simple transformation for demonstration
        return {
            "keys_processed": list(input_data.keys()),
            "value_count": len(input_data),
            "transformed": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
