"""
Tests for the embeddings service.
"""
import pytest
import numpy as np
from src.core.embeddings import EmbeddingService


def test_embedding_service_initialization():
    """Test that embedding service initializes correctly."""
    service = EmbeddingService()
    assert service.model is not None
    assert service.get_embedding_dimension() > 0


def test_embed_text():
    """Test single text embedding."""
    service = EmbeddingService()
    text = "How do I reset my password?"
    
    embedding = service.embed_text(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == service.get_embedding_dimension()
    assert not np.isnan(embedding).any()


def test_embed_batch():
    """Test batch text embedding."""
    service = EmbeddingService()
    texts = [
        "How do I reset my password?",
        "What are your business hours?",
        "How can I track my order?"
    ]
    
    embeddings = service.embed_batch(texts)
    
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] == service.get_embedding_dimension()
    assert not np.isnan(embeddings).any()


def test_similarity():
    """Test similarity calculation."""
    service = EmbeddingService()
    
    text1 = "How do I reset my password?"
    text2 = "I forgot my password"
    text3 = "What are your business hours?"
    
    emb1 = service.embed_text(text1)
    emb2 = service.embed_text(text2)
    emb3 = service.embed_text(text3)
    
    # Normalize for fair comparison
    emb1 = emb1 / np.linalg.norm(emb1)
    emb2 = emb2 / np.linalg.norm(emb2)
    emb3 = emb3 / np.linalg.norm(emb3)
    
    sim_12 = service.similarity(emb1, emb2)
    sim_13 = service.similarity(emb1, emb3)
    
    # Similar texts should have higher similarity
    assert sim_12 > sim_13
    assert 0 <= sim_12 <= 1
    assert 0 <= sim_13 <= 1


def test_embedding_consistency():
    """Test that same text produces same embedding."""
    service = EmbeddingService()
    text = "How do I reset my password?"
    
    emb1 = service.embed_text(text)
    emb2 = service.embed_text(text)
    
    np.testing.assert_array_almost_equal(emb1, emb2)
