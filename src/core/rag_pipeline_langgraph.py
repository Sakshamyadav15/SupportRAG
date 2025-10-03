"""
Enhanced RAG Pipeline using LangGraph for orchestration.
This is an alternative to the basic rag_pipeline.py with more sophisticated flow control.
"""
import time
import uuid
from typing import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph

from src.core.vectordb import get_vector_db
from src.core.llm import get_llm_service
from src.models.schemas import QueryRequest, QueryResponse, Citation, EscalationReason
from src.config import settings
from src.utils.logger import get_logger
from src.utils.metrics import MetricsTracker

logger = get_logger(__name__)


# Define state for the graph
class RAGState(TypedDict):
    """State for the RAG application using LangGraph."""
    question: str
    context: List[dict]  # Retrieved documents
    answer: str
    confidence_score: float
    escalated: bool
    query_id: str
    latency_ms: float


class LangGraphRAGPipeline:
    """Enhanced RAG pipeline using LangGraph for orchestration."""
    
    def __init__(self):
        """Initialize the LangGraph RAG pipeline."""
        self.vector_db = get_vector_db()
        self.llm_service = get_llm_service()
        self.metrics_tracker = MetricsTracker()
        self.confidence_threshold = settings.confidence_threshold
        
        # Build the graph
        self.graph = self._build_graph()
        logger.info("Initialized LangGraph RAG pipeline")
    
    def _retrieve(self, state: RAGState) -> dict:
        """
        Retrieval step: Search for relevant FAQs.
        
        Args:
            state: Current state containing the question
            
        Returns:
            Updated state with retrieved context
        """
        logger.info(f"Retrieving documents for: {state['question']}")
        
        results = self.vector_db.search(
            state["question"],
            top_k=settings.top_k_results
        )
        
        # Convert to dict format for state
        context = []
        for faq, score in results:
            context.append({
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category,
                "score": float(score)
            })
        
        confidence = context[0]["score"] if context else 0.0
        
        return {
            "context": context,
            "confidence_score": confidence
        }
    
    def _check_confidence(self, state: RAGState) -> dict:
        """
        Check if confidence is high enough to proceed with generation.
        
        Args:
            state: Current state with confidence score
            
        Returns:
            Updated state with escalation flag
        """
        if not state["context"] or state["confidence_score"] < self.confidence_threshold:
            logger.warning(f"Low confidence: {state['confidence_score']:.2f}")
            return {
                "escalated": True,
                "answer": "I'm not confident enough to answer this question. Escalating to a human agent..."
            }
        
        return {"escalated": False}
    
    def _generate(self, state: RAGState) -> dict:
        """
        Generation step: Create answer using LLM.
        
        Args:
            state: Current state with question and context
            
        Returns:
            Updated state with generated answer
        """
        if state.get("escalated", False):
            # Skip generation if escalated
            return {}
        
        logger.info("Generating answer with LLM")
        
        # Format context for the LLM
        context_str = "\n\n".join([
            f"FAQ {i+1} (Relevance: {doc['score']:.2f}):\n"
            f"Q: {doc['question']}\n"
            f"A: {doc['answer']}"
            for i, doc in enumerate(state["context"])
        ])
        
        try:
            answer = self.llm_service.generate_answer(
                question=state["question"],
                context=context_str
            )
            return {"answer": answer}
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "escalated": True,
                "answer": "An error occurred while generating the answer. Escalating to a human agent..."
            }
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph.
        
        Returns:
            Compiled state graph
        """
        # Create state graph
        graph_builder = StateGraph(RAGState)
        
        # Add nodes (steps)
        graph_builder.add_node("retrieve", self._retrieve)
        graph_builder.add_node("check_confidence", self._check_confidence)
        graph_builder.add_node("generate", self._generate)
        
        # Define edges (flow)
        graph_builder.add_edge(START, "retrieve")
        graph_builder.add_edge("retrieve", "check_confidence")
        graph_builder.add_edge("check_confidence", "generate")
        
        # Compile the graph
        return graph_builder.compile()
    
    def query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a user query using the LangGraph pipeline.
        
        Args:
            request: Query request object
            
        Returns:
            QueryResponse with answer and citations
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        logger.info(f"Processing query {query_id}: {request.question}")
        
        # Initial state
        initial_state = RAGState(
            question=request.question,
            context=[],
            answer="",
            confidence_score=0.0,
            escalated=False,
            query_id=query_id,
            latency_ms=0.0
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Create citations
        citations = [
            Citation(
                faq_id=doc["id"],
                question=doc["question"],
                answer=doc["answer"],
                similarity_score=doc["score"],
                category=doc.get("category")
            )
            for doc in result.get("context", [])
        ]
        
        # Create response
        response = QueryResponse(
            answer=result.get("answer", "No answer generated"),
            citations=citations,
            confidence_score=result.get("confidence_score", 0.0),
            escalated=result.get("escalated", False),
            latency_ms=latency_ms,
            query_id=query_id
        )
        
        # Track metrics
        self.metrics_tracker.log_query(
            query_id=query_id,
            question=request.question,
            answer=response.answer,
            confidence_score=response.confidence_score,
            escalated=response.escalated,
            latency_ms=latency_ms,
            citations_count=len(citations)
        )
        
        logger.info(f"Query {query_id} completed in {latency_ms:.2f}ms")
        return response


# Global LangGraph RAG pipeline instance
_langgraph_rag_pipeline = None


def get_langgraph_rag_pipeline() -> LangGraphRAGPipeline:
    """
    Get or create the global LangGraph RAG pipeline instance.
    
    Returns:
        LangGraphRAGPipeline instance
    """
    global _langgraph_rag_pipeline
    if _langgraph_rag_pipeline is None:
        _langgraph_rag_pipeline = LangGraphRAGPipeline()
    return _langgraph_rag_pipeline
