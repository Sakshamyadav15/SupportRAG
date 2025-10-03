"""
RAG Pipeline - Orchestrates retrieval and generation for query answering.
Core logic for the SupportRAG application.
"""
import time
import uuid
from typing import List, Optional
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    Citation,
    FAQItem,
    EscalationReason
)
from src.core.vectordb import get_vector_db
from src.core.llm import get_llm_service
from src.config import settings
from src.utils.logger import get_logger
from src.utils.metrics import MetricsTracker

logger = get_logger(__name__)


class RAGPipeline:
    """RAG pipeline for question answering with FAQ retrieval."""
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        self.vector_db = get_vector_db()
        self.llm_service = get_llm_service()
        self.metrics_tracker = MetricsTracker()
        self.confidence_threshold = settings.confidence_threshold
        logger.info("Initialized RAG pipeline")
    
    def query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a user query and generate a response.
        
        Args:
            request: Query request object
            
        Returns:
            QueryResponse with answer and citations
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        logger.info(f"Processing query {query_id}: {request.question}")
        
        # Retrieve relevant FAQs
        retrieval_results = self.vector_db.search(
            request.question,
            top_k=request.top_k or settings.top_k_results
        )
        
        # Check if we have results
        if not retrieval_results:
            return self._create_escalation_response(
                query_id=query_id,
                question=request.question,
                reason=EscalationReason.NO_RESULTS,
                latency_ms=(time.time() - start_time) * 1000
            )
        
        # Get top result confidence
        top_score = retrieval_results[0][1]
        
        # Check confidence threshold
        if top_score < self.confidence_threshold:
            return self._create_escalation_response(
                query_id=query_id,
                question=request.question,
                reason=EscalationReason.LOW_CONFIDENCE,
                latency_ms=(time.time() - start_time) * 1000,
                citations=self._create_citations(retrieval_results)
            )
        
        # Generate answer using LLM
        try:
            context = self._format_context(retrieval_results)
            answer = self.llm_service.generate_answer(
                question=request.question,
                context=context
            )
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return self._create_escalation_response(
                query_id=query_id,
                question=request.question,
                reason=EscalationReason.LOW_CONFIDENCE,
                latency_ms=(time.time() - start_time) * 1000
            )
        
        # Create response
        latency_ms = (time.time() - start_time) * 1000
        citations = self._create_citations(retrieval_results)
        
        response = QueryResponse(
            answer=answer,
            citations=citations,
            confidence_score=top_score,
            escalated=False,
            latency_ms=latency_ms,
            query_id=query_id
        )
        
        # Track metrics
        self.metrics_tracker.log_query(
            query_id=query_id,
            question=request.question,
            answer=answer,
            confidence_score=top_score,
            escalated=False,
            latency_ms=latency_ms,
            citations_count=len(citations)
        )
        
        logger.info(f"Query {query_id} completed in {latency_ms:.2f}ms")
        return response
    
    def _format_context(self, retrieval_results: List[tuple]) -> str:
        """
        Format retrieval results into context string.
        
        Args:
            retrieval_results: List of (FAQ, score) tuples
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, (faq, score) in enumerate(retrieval_results, 1):
            context_parts.append(
                f"FAQ {i} (Relevance: {score:.2f}):\n"
                f"Q: {faq.question}\n"
                f"A: {faq.answer}\n"
            )
        return "\n".join(context_parts)
    
    def _create_citations(self, retrieval_results: List[tuple]) -> List[Citation]:
        """
        Create citation objects from retrieval results.
        
        Args:
            retrieval_results: List of (FAQ, score) tuples
            
        Returns:
            List of Citation objects
        """
        citations = []
        for faq, score in retrieval_results:
            citation = Citation(
                faq_id=faq.id,
                question=faq.question,
                answer=faq.answer,
                similarity_score=score,
                category=faq.category
            )
            citations.append(citation)
        return citations
    
    def _create_escalation_response(
        self,
        query_id: str,
        question: str,
        reason: EscalationReason,
        latency_ms: float,
        citations: Optional[List[Citation]] = None
    ) -> QueryResponse:
        """
        Create an escalation response.
        
        Args:
            query_id: Query identifier
            question: User's question
            reason: Escalation reason
            latency_ms: Response latency
            citations: Optional citations
            
        Returns:
            QueryResponse with escalation
        """
        escalation_messages = {
            EscalationReason.NO_RESULTS: "I couldn't find any relevant FAQs for your question. Escalating to a human agent...",
            EscalationReason.LOW_CONFIDENCE: "I'm not confident enough to answer this question. Escalating to a human agent...",
            EscalationReason.AMBIGUOUS: "Your question seems ambiguous. Escalating to a human agent...",
            EscalationReason.EXPLICIT_REQUEST: "Connecting you with a human agent..."
        }
        
        response = QueryResponse(
            answer=escalation_messages.get(reason, "Escalating to human agent..."),
            citations=citations or [],
            confidence_score=0.0,
            escalated=True,
            latency_ms=latency_ms,
            query_id=query_id
        )
        
        # Track escalation
        self.metrics_tracker.log_query(
            query_id=query_id,
            question=question,
            answer=response.answer,
            confidence_score=0.0,
            escalated=True,
            escalation_reason=reason,
            latency_ms=latency_ms,
            citations_count=len(citations) if citations else 0
        )
        
        logger.warning(f"Query {query_id} escalated: {reason}")
        return response
    
    def add_faq(self, faq: FAQItem) -> str:
        """
        Add a new FAQ to the database.
        
        Args:
            faq: FAQ item to add
            
        Returns:
            FAQ ID
        """
        faq_id = self.vector_db.add_faq(faq)
        logger.info(f"Added new FAQ: {faq_id}")
        return faq_id
    
    def get_metrics(self):
        """Get current metrics."""
        return self.metrics_tracker.get_metrics()


# Global RAG pipeline instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create the global RAG pipeline instance.
    
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
