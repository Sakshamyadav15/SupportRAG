"""
Enhanced FastAPI application with dual vector store support
Endpoints for ingestion and querying with fallback logic
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from src.core.dual_rag_pipeline import get_dual_rag_pipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Request/Response Models
class IngestRequest(BaseModel):
    """Request to trigger vector store ingestion"""
    rebuild: bool = Field(
        default=False,
        description="If True, rebuild stores from scratch. If False, load existing."
    )


class IngestResponse(BaseModel):
    """Response from ingestion endpoint"""
    status: str
    faq_count: int
    ticket_count: int
    message: str


class QueryRequest(BaseModel):
    """Request for querying the RAG system"""
    question: str = Field(..., description="User's question")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results to retrieve")


class Citation(BaseModel):
    """Citation/source information"""
    rank: int
    content: str
    similarity: float
    source: str
    category: str
    resolution_status: str | None = None


class QueryResponse(BaseModel):
    """Response from query endpoint"""
    answer: str
    source: str
    confidence: float
    citations: List[Citation]
    latency_ms: float
    query: str
    timestamp: str


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Enhanced SupportRAG API with Dual Vector Stores...")
    
    # Initialize pipeline
    pipeline = get_dual_rag_pipeline()
    
    # Try to load existing stores
    try:
        pipeline.load_vector_stores()
        logger.info("Loaded existing vector stores")
    except Exception as e:
        logger.warning(f"Could not load existing stores: {e}")
        logger.info("Run POST /ingest to build vector stores")
    
    logger.info("API ready to serve requests")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enhanced SupportRAG API...")


# Create FastAPI app
app = FastAPI(
    title="SupportRAG Enhanced API",
    description="Dual vector store RAG system with FAQ and Ticket fallback",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SupportRAG Enhanced API with Dual Vector Stores",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "ingest": "/ingest (POST)",
            "query": "/query (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    pipeline = get_dual_rag_pipeline()
    
    return {
        "status": "healthy",
        "faq_store_loaded": pipeline.faq_store is not None,
        "ticket_store_loaded": pipeline.ticket_store is not None,
        "faq_threshold": pipeline.faq_threshold
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest):
    """
    Ingest data and build vector stores
    
    - Loads support_faqs.csv
    - Loads HuggingFace dataset MakTek/Customer_support_faqs_dataset
    - Loads support_tickets.csv
    - Builds FAQ and Ticket FAISS vector stores
    - Saves stores to disk
    """
    try:
        pipeline = get_dual_rag_pipeline()
        
        if request.rebuild:
            logger.info("Rebuilding vector stores from scratch...")
            pipeline.build_vector_stores()
            pipeline.save_vector_stores()
        else:
            logger.info("Loading existing vector stores...")
            try:
                pipeline.load_vector_stores()
            except Exception as e:
                logger.warning(f"Could not load existing stores: {e}. Building new ones...")
                pipeline.build_vector_stores()
                pipeline.save_vector_stores()
        
        # Count documents (approximate)
        faq_count = len(pipeline.load_support_faqs()) + len(pipeline.load_huggingface_faqs())
        ticket_count = len(pipeline.load_support_tickets())
        
        return IngestResponse(
            status="success",
            faq_count=faq_count,
            ticket_count=ticket_count,
            message=f"Vector stores built successfully. FAQ: {faq_count}, Tickets: {ticket_count}"
        )
    
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with dual vector store fallback (ASYNC)
    
    Logic:
    1. Search FAQ and Ticket stores in parallel
    2. Use FAQ if similarity >= 0.65, else fallback to Ticket
    3. Generate answer with async LLM call
    4. Return answer + metadata (source, citations, status)
    
    Performance optimizations:
    - Parallel vector store searches
    - Async LLM generation
    - Non-blocking I/O operations
    """
    try:
        pipeline = get_dual_rag_pipeline()
        
        if not pipeline.faq_store and not pipeline.ticket_store:
            raise HTTPException(
                status_code=503,
                detail="Vector stores not initialized. Run POST /ingest first."
            )
        
        # Execute async query with parallel retrieval
        result = await pipeline.aquery(
            question=request.question,
            top_k=request.top_k
        )
        
        # Convert to response model
        citations = [
            Citation(**citation) for citation in result["citations"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            source=result["source"],
            confidence=result["confidence"],
            citations=citations,
            latency_ms=result["latency_ms"],
            query=result["query"],
            timestamp=result["timestamp"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    import json
    from pathlib import Path
    
    log_file = Path("logs/query_logs.jsonl")
    
    if not log_file.exists():
        return {
            "total_queries": 0,
            "avg_latency_ms": 0,
            "avg_confidence": 0,
            "source_breakdown": {}
        }
    
    # Read logs
    queries = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            queries.append(json.loads(line))
    
    if not queries:
        return {
            "total_queries": 0,
            "avg_latency_ms": 0,
            "avg_confidence": 0,
            "source_breakdown": {}
        }
    
    # Calculate stats
    total = len(queries)
    avg_latency = sum(q["latency_ms"] for q in queries) / total
    avg_confidence = sum(q["confidence"] for q in queries) / total
    
    # Source breakdown
    sources = {}
    for q in queries:
        source = q["source"]
        sources[source] = sources.get(source, 0) + 1
    
    return {
        "total_queries": total,
        "avg_latency_ms": round(avg_latency, 2),
        "avg_confidence": round(avg_confidence, 4),
        "source_breakdown": sources
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
