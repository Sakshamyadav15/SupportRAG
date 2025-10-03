"""
Metrics tracking and logging utility.
Tracks query performance, escalations, and system metrics.
"""
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from src.config import settings
from src.models.schemas import EscalationReason


class MetricsTracker:
    """Tracks and logs application metrics."""
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.start_time = time.time()
        self.metrics = {
            'total_queries': 0,
            'escalated_queries': 0,
            'total_latency_ms': 0.0,
            'total_confidence': 0.0,
            'queries': []
        }
        self.metrics_path = settings.get_metrics_file_path()
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_metrics()
    
    def log_query(
        self,
        query_id: str,
        question: str,
        answer: str,
        confidence_score: float,
        escalated: bool,
        latency_ms: float,
        citations_count: int,
        escalation_reason: Optional[EscalationReason] = None,
        user_id: Optional[str] = None
    ):
        """
        Log a query and its results.
        
        Args:
            query_id: Unique query identifier
            question: User's question
            answer: Generated answer
            confidence_score: Confidence score
            escalated: Whether query was escalated
            latency_ms: Response latency in milliseconds
            citations_count: Number of citations
            escalation_reason: Reason for escalation if applicable
            user_id: Optional user identifier
        """
        entry = {
            'query_id': query_id,
            'question': question,
            'answer': answer,
            'confidence_score': confidence_score,
            'escalated': escalated,
            'escalation_reason': escalation_reason.value if escalation_reason else None,
            'latency_ms': latency_ms,
            'citations_count': citations_count,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Update aggregates
        self.metrics['total_queries'] += 1
        if escalated:
            self.metrics['escalated_queries'] += 1
        self.metrics['total_latency_ms'] += latency_ms
        self.metrics['total_confidence'] += confidence_score
        
        # Append query
        self.metrics['queries'].append(entry)
        
        # Save periodically (every 10 queries)
        if self.metrics['total_queries'] % 10 == 0:
            self._save_metrics()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics summary.
        
        Returns:
            Dictionary of current metrics
        """
        total = self.metrics['total_queries']
        
        if total == 0:
            return {
                'total_queries': 0,
                'escalation_rate': 0.0,
                'average_latency_ms': 0.0,
                'average_confidence': 0.0,
                'uptime_seconds': time.time() - self.start_time
            }
        
        return {
            'total_queries': total,
            'escalation_rate': (self.metrics['escalated_queries'] / total) * 100,
            'average_latency_ms': self.metrics['total_latency_ms'] / total,
            'average_confidence': self.metrics['total_confidence'] / total,
            'uptime_seconds': time.time() - self.start_time
        }
    
    def _save_metrics(self):
        """Save metrics to disk."""
        try:
            with open(self.metrics_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            # Don't fail if we can't save metrics
            print(f"Warning: Could not save metrics: {e}")
    
    def _load_metrics(self):
        """Load metrics from disk if available."""
        try:
            if self.metrics_path.exists():
                with open(self.metrics_path, 'r') as f:
                    loaded = json.load(f)
                    # Only load aggregates, not all historical queries
                    self.metrics['total_queries'] = loaded.get('total_queries', 0)
                    self.metrics['escalated_queries'] = loaded.get('escalated_queries', 0)
                    self.metrics['total_latency_ms'] = loaded.get('total_latency_ms', 0.0)
                    self.metrics['total_confidence'] = loaded.get('total_confidence', 0.0)
        except Exception:
            # Start fresh if we can't load
            pass
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {
            'total_queries': 0,
            'escalated_queries': 0,
            'total_latency_ms': 0.0,
            'total_confidence': 0.0,
            'queries': []
        }
        self._save_metrics()
