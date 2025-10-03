"""
Tests for the vector database.
"""
import pytest
from src.core.vectordb import VectorDatabase
from src.models.schemas import FAQItem


@pytest.fixture
def vector_db():
    """Create a fresh vector database for testing."""
    db = VectorDatabase()
    db.clear()
    return db


@pytest.fixture
def sample_faqs():
    """Create sample FAQ items."""
    return [
        FAQItem(
            id="test_001",
            question="How do I reset my password?",
            answer="Go to settings and click forgot password.",
            category="account"
        ),
        FAQItem(
            id="test_002",
            question="What are your business hours?",
            answer="We are open Monday to Friday 9 AM to 5 PM.",
            category="general"
        ),
        FAQItem(
            id="test_003",
            question="How can I track my order?",
            answer="Log into your account and check order status.",
            category="orders"
        )
    ]


def test_add_single_faq(vector_db, sample_faqs):
    """Test adding a single FAQ."""
    faq = sample_faqs[0]
    faq_id = vector_db.add_faq(faq)
    
    assert faq_id is not None
    assert vector_db.get_total_faqs() == 1


def test_add_batch_faqs(vector_db, sample_faqs):
    """Test adding multiple FAQs."""
    faq_ids = vector_db.add_faqs_batch(sample_faqs)
    
    assert len(faq_ids) == len(sample_faqs)
    assert vector_db.get_total_faqs() == len(sample_faqs)


def test_search_relevant_results(vector_db, sample_faqs):
    """Test that search returns relevant results."""
    vector_db.add_faqs_batch(sample_faqs)
    
    query = "I forgot my password"
    results = vector_db.search(query, top_k=2)
    
    assert len(results) > 0
    assert len(results) <= 2
    
    # Check that results are sorted by score
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)
    
    # Top result should be the password reset FAQ
    top_faq, top_score = results[0]
    assert "password" in top_faq.question.lower()


def test_search_empty_database(vector_db):
    """Test searching an empty database."""
    results = vector_db.search("test query")
    assert len(results) == 0


def test_search_top_k(vector_db, sample_faqs):
    """Test that top_k parameter works correctly."""
    vector_db.add_faqs_batch(sample_faqs)
    
    results_1 = vector_db.search("test", top_k=1)
    results_2 = vector_db.search("test", top_k=2)
    
    assert len(results_1) == 1
    assert len(results_2) == 2


def test_clear_database(vector_db, sample_faqs):
    """Test clearing the database."""
    vector_db.add_faqs_batch(sample_faqs)
    assert vector_db.get_total_faqs() > 0
    
    vector_db.clear()
    assert vector_db.get_total_faqs() == 0
