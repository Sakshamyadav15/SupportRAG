"""
Example usage of SupportRAG programmatically.
Demonstrates how to use the RAG system without the API.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.rag_pipeline import get_rag_pipeline
from src.models.schemas import QueryRequest, FAQItem


def example_basic_query():
    """Example: Basic query to the RAG system."""
    print("=" * 60)
    print("Example 1: Basic Query")
    print("=" * 60)
    
    rag = get_rag_pipeline()
    
    request = QueryRequest(
        question="How do I reset my password?",
        top_k=3
    )
    
    response = rag.query(request)
    
    print(f"\nQuestion: {request.question}")
    print(f"\nAnswer: {response.answer}")
    print(f"\nConfidence: {response.confidence_score:.2%}")
    print(f"Escalated: {response.escalated}")
    print(f"Latency: {response.latency_ms:.2f}ms")
    
    print(f"\nCitations ({len(response.citations)}):")
    for i, citation in enumerate(response.citations, 1):
        print(f"\n  {i}. {citation.question}")
        print(f"     Similarity: {citation.similarity_score:.2%}")


def example_multiple_queries():
    """Example: Process multiple queries."""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Queries")
    print("=" * 60)
    
    rag = get_rag_pipeline()
    
    questions = [
        "Where is my order?",
        "What payment methods do you accept?",
        "How do I cancel my subscription?",
    ]
    
    for question in questions:
        request = QueryRequest(question=question, top_k=2)
        response = rag.query(request)
        
        print(f"\nQ: {question}")
        print(f"A: {response.answer[:100]}...")
        print(f"Confidence: {response.confidence_score:.2%}")


def example_add_faq():
    """Example: Add a new FAQ programmatically."""
    print("\n" + "=" * 60)
    print("Example 3: Add New FAQ")
    print("=" * 60)
    
    rag = get_rag_pipeline()
    
    new_faq = FAQItem(
        question="What is your data retention policy?",
        answer="We retain customer data for 7 years as required by law. "
               "You can request deletion of your data at any time by contacting privacy@company.com",
        category="privacy",
        tags=["privacy", "data", "gdpr"]
    )
    
    faq_id = rag.add_faq(new_faq)
    print(f"\nAdded new FAQ with ID: {faq_id}")
    
    # Query the new FAQ
    request = QueryRequest(question="How long do you keep my data?", top_k=1)
    response = rag.query(request)
    
    print(f"\nTest Query: {request.question}")
    print(f"Answer: {response.answer}")


def example_check_metrics():
    """Example: Get system metrics."""
    print("\n" + "=" * 60)
    print("Example 4: System Metrics")
    print("=" * 60)
    
    rag = get_rag_pipeline()
    metrics = rag.get_metrics()
    
    print(f"\nTotal Queries: {metrics['total_queries']}")
    print(f"Escalation Rate: {metrics['escalation_rate']:.2f}%")
    print(f"Average Latency: {metrics['average_latency_ms']:.2f}ms")
    print(f"Average Confidence: {metrics['average_confidence']:.2%}")
    print(f"Uptime: {metrics['uptime_seconds']:.0f}s")


def example_low_confidence():
    """Example: Query that triggers escalation."""
    print("\n" + "=" * 60)
    print("Example 5: Low Confidence Escalation")
    print("=" * 60)
    
    rag = get_rag_pipeline()
    
    # Query something not in the FAQ database
    request = QueryRequest(
        question="What is the meaning of life?",
        top_k=3
    )
    
    response = rag.query(request)
    
    print(f"\nQuestion: {request.question}")
    print(f"Answer: {response.answer}")
    print(f"Escalated: {response.escalated}")
    print(f"Confidence: {response.confidence_score:.2%}")


def example_with_citations():
    """Example: Display detailed citations."""
    print("\n" + "=" * 60)
    print("Example 6: Detailed Citations")
    print("=" * 60)
    
    rag = get_rag_pipeline()
    
    request = QueryRequest(
        question="How can I contact support?",
        top_k=3
    )
    
    response = rag.query(request)
    
    print(f"\nQuestion: {request.question}")
    print(f"\nAnswer: {response.answer}\n")
    
    print("Sources:")
    for i, citation in enumerate(response.citations, 1):
        print(f"\n[{i}] FAQ ID: {citation.faq_id}")
        print(f"    Category: {citation.category}")
        print(f"    Relevance: {citation.similarity_score:.2%}")
        print(f"    Q: {citation.question}")
        print(f"    A: {citation.answer}")


def main():
    """Run all examples."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          SupportRAG - Example Usage Demonstrations        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        # Run examples
        example_basic_query()
        example_multiple_queries()
        example_add_faq()
        example_check_metrics()
        example_low_confidence()
        example_with_citations()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("1. Initialized the vector database: python scripts/init_vectordb.py")
        print("2. Set your API key in .env file")
        print("3. Installed all dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
