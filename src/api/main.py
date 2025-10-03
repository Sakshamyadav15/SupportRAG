"""
FastAPI application for SupportRAG.
Provides RESTful API endpoints for the RAG system.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from src.config import settings
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    FAQAddRequest,
    FAQAddResponse,
    FAQItem,
    MetricsResponse,
    HealthResponse
)
from src.core.rag_pipeline import get_rag_pipeline
from src.core.vectordb import get_vector_db
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting SupportRAG API...")
    
    # Validate API keys
    if not settings.validate_api_keys():
        logger.warning("API keys not configured properly. Some features may not work.")
    
    # Initialize RAG pipeline (loads vector DB)
    try:
        _ = get_rag_pipeline()
        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SupportRAG API...")
    
    # Save vector database
    try:
        vector_db = get_vector_db()
        vector_db.save()
        logger.info("Vector database saved")
    except Exception as e:
        logger.error(f"Failed to save vector database: {e}")


# Create FastAPI app
app = FastAPI(
    title="SupportRAG API",
    description="Retrieval-Augmented Generation API for Customer Support FAQs",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check system health and component status."""
    checks = {}
    
    # Check vector DB
    try:
        vector_db = get_vector_db()
        checks['vector_db'] = vector_db.get_total_faqs() > 0
    except Exception:
        checks['vector_db'] = False
    
    # Check LLM
    try:
        from src.core.llm import get_llm_service
        _ = get_llm_service()
        checks['llm'] = True
    except Exception:
        checks['llm'] = False
    
    return HealthResponse(
        status="healthy" if all(checks.values()) else "degraded",
        version="1.0.0",
        checks=checks
    )


# Query endpoint
@app.post(
    f"{settings.api_prefix}/query",
    response_model=QueryResponse,
    tags=["RAG"],
    summary="Query the RAG system"
)
async def query_rag(request: QueryRequest):
    """
    Process a user query and return an AI-generated answer with citations.
    
    - **question**: The user's question
    - **top_k**: Number of similar FAQs to retrieve (default: 3)
    - **user_id**: Optional user identifier for tracking
    """
    try:
        rag_pipeline = get_rag_pipeline()
        response = rag_pipeline.query(request)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


# Add FAQ endpoint
@app.post(
    f"{settings.api_prefix}/faq",
    response_model=FAQAddResponse,
    tags=["FAQ Management"],
    summary="Add a new FAQ"
)
async def add_faq(request: FAQAddRequest):
    """
    Add a new FAQ to the knowledge base.
    
    - **question**: The FAQ question
    - **answer**: The FAQ answer
    - **category**: Optional category (default: "general")
    - **tags**: Optional list of tags
    """
    try:
        faq = FAQItem(
            question=request.question,
            answer=request.answer,
            category=request.category,
            tags=request.tags
        )
        
        rag_pipeline = get_rag_pipeline()
        faq_id = rag_pipeline.add_faq(faq)
        
        # Save vector database
        vector_db = get_vector_db()
        vector_db.save()
        
        return FAQAddResponse(
            success=True,
            faq_id=faq_id,
            message="FAQ added successfully"
        )
    except Exception as e:
        logger.error(f"Error adding FAQ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add FAQ: {str(e)}"
        )


# Get metrics endpoint
@app.get(
    f"{settings.api_prefix}/metrics",
    response_model=MetricsResponse,
    tags=["System"],
    summary="Get system metrics"
)
async def get_metrics():
    """
    Get current system metrics including query statistics and performance.
    
    Returns metrics such as:
    - Total queries processed
    - Escalation rate
    - Average latency
    - Average confidence score
    - System uptime
    """
    try:
        rag_pipeline = get_rag_pipeline()
        metrics = rag_pipeline.get_metrics()
        
        vector_db = get_vector_db()
        total_faqs = vector_db.get_total_faqs()
        
        return MetricsResponse(
            total_queries=metrics['total_queries'],
            escalation_rate=metrics['escalation_rate'],
            average_latency_ms=metrics['average_latency_ms'],
            average_confidence=metrics['average_confidence'],
            total_faqs=total_faqs,
            uptime_seconds=metrics['uptime_seconds']
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SupportRAG API",
        "version": "1.0.0",
        "description": "Retrieval-Augmented Generation API for Customer Support",
        "docs_url": "/docs",
        "health_url": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
