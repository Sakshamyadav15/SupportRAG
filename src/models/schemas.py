"""
Data models for SupportRAG application.
Defines Pydantic models for API requests/responses and internal data structures.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QueryRequest(BaseModel):
    """Request model for user queries."""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of results to retrieve")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or only whitespace')
        return v.strip()


class Citation(BaseModel):
    """Citation reference to source FAQ."""
    faq_id: str = Field(..., description="Unique FAQ identifier")
    question: str = Field(..., description="Original FAQ question")
    answer: str = Field(..., description="FAQ answer")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    category: Optional[str] = Field(None, description="FAQ category")


class QueryResponse(BaseModel):
    """Response model for query results."""
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    escalated: bool = Field(False, description="Whether query was escalated")
    latency_ms: float = Field(..., description="Response time in milliseconds")
    query_id: str = Field(..., description="Unique query identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FAQItem(BaseModel):
    """Model for FAQ entries."""
    id: Optional[str] = Field(None, description="Unique identifier")
    question: str = Field(..., min_length=1, description="FAQ question")
    answer: str = Field(..., min_length=1, description="FAQ answer")
    category: Optional[str] = Field("general", description="FAQ category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    @validator('question', 'answer')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text fields cannot be empty')
        return v.strip()


class FAQAddRequest(BaseModel):
    """Request model for adding new FAQ."""
    question: str = Field(..., min_length=1, description="FAQ question")
    answer: str = Field(..., min_length=1, description="FAQ answer")
    category: Optional[str] = Field("general", description="FAQ category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional tags")


class FAQAddResponse(BaseModel):
    """Response model for FAQ addition."""
    success: bool = Field(..., description="Whether operation succeeded")
    faq_id: str = Field(..., description="ID of added FAQ")
    message: str = Field(..., description="Status message")


class MetricsResponse(BaseModel):
    """Response model for system metrics."""
    total_queries: int = Field(..., description="Total queries processed")
    escalation_rate: float = Field(..., description="Percentage of escalated queries")
    average_latency_ms: float = Field(..., description="Average response latency")
    average_confidence: float = Field(..., description="Average confidence score")
    total_faqs: int = Field(..., description="Total FAQs in database")
    uptime_seconds: float = Field(..., description="System uptime in seconds")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, bool] = Field(default_factory=dict, description="Component health checks")


class EscalationReason(str, Enum):
    """Enumeration of escalation reasons."""
    LOW_CONFIDENCE = "low_confidence"
    NO_RESULTS = "no_results"
    AMBIGUOUS = "ambiguous"
    EXPLICIT_REQUEST = "explicit_request"


class LogEntry(BaseModel):
    """Model for query log entries."""
    query_id: str
    question: str
    answer: str
    confidence_score: float
    escalated: bool
    escalation_reason: Optional[EscalationReason] = None
    latency_ms: float
    top_k: int
    citations_count: int
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
