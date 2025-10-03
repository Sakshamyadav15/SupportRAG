"""
Tests for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.vectordb import get_vector_db
from src.models.schemas import FAQItem

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_data():
    """Setup test data before each test."""
    vector_db = get_vector_db()
    vector_db.clear()
    
    # Add some test FAQs
    test_faqs = [
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
        )
    ]
    vector_db.add_faqs_batch(test_faqs)
    yield
    vector_db.clear()


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_query_endpoint():
    """Test query endpoint with valid question."""
    payload = {
        "question": "How do I reset my password?",
        "top_k": 3
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "confidence_score" in data
    assert "escalated" in data
    assert "latency_ms" in data
    assert "query_id" in data


def test_query_endpoint_invalid_request():
    """Test query endpoint with invalid request."""
    payload = {
        "question": "",  # Empty question
        "top_k": 3
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 422  # Validation error


def test_add_faq_endpoint():
    """Test adding a new FAQ."""
    payload = {
        "question": "Test question?",
        "answer": "Test answer.",
        "category": "test"
    }
    response = client.post("/api/v1/faq", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "faq_id" in data
    assert "message" in data


def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_queries" in data
    assert "escalation_rate" in data
    assert "average_latency_ms" in data
    assert "average_confidence" in data
    assert "total_faqs" in data
    assert "uptime_seconds" in data
