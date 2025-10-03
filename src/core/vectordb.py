"""
Vector database service using FAISS for similarity search.
Manages FAQ storage, indexing, and retrieval.
"""
from typing import List, Tuple, Optional
import numpy as np
import faiss
import pickle
import json
from pathlib import Path
from src.models.schemas import FAQItem
from src.core.embeddings import get_embedding_service
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VectorDatabase:
    """FAISS-based vector database for FAQ storage and retrieval."""
    
    def __init__(self, dimension: int = None):
        """
        Initialize the vector database.
        
        Args:
            dimension: Embedding dimension (auto-detected if not provided)
        """
        self.embedding_service = get_embedding_service()
        self.dimension = dimension or self.embedding_service.get_embedding_dimension()
        self.index = None
        self.faqs: List[FAQItem] = []
        self.db_path = settings.get_vector_db_full_path()
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index."""
        # Using IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        logger.info(f"Initialized FAISS index with dimension {self.dimension}")
    
    def add_faq(self, faq: FAQItem) -> str:
        """
        Add a single FAQ to the database.
        
        Args:
            faq: FAQ item to add
            
        Returns:
            FAQ ID
        """
        # Generate ID if not provided
        if not faq.id:
            faq.id = f"faq_{len(self.faqs):05d}"
        
        # Generate embedding
        text = f"{faq.question} {faq.answer}"
        embedding = self.embedding_service.embed_text(text)
        
        # Normalize for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add to index
        self.index.add(np.array([embedding], dtype=np.float32))
        self.faqs.append(faq)
        
        logger.info(f"Added FAQ: {faq.id}")
        return faq.id
    
    def add_faqs_batch(self, faqs: List[FAQItem]) -> List[str]:
        """
        Add multiple FAQs to the database.
        
        Args:
            faqs: List of FAQ items to add
            
        Returns:
            List of FAQ IDs
        """
        # Generate IDs for FAQs without them
        for i, faq in enumerate(faqs):
            if not faq.id:
                faq.id = f"faq_{len(self.faqs) + i:05d}"
        
        # Generate embeddings in batch
        texts = [f"{faq.question} {faq.answer}" for faq in faqs]
        embeddings = self.embedding_service.embed_batch(texts)
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        # Add to index
        self.index.add(embeddings.astype(np.float32))
        self.faqs.extend(faqs)
        
        logger.info(f"Added {len(faqs)} FAQs to database")
        return [faq.id for faq in faqs]
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[FAQItem, float]]:
        """
        Search for similar FAQs.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of (FAQ, similarity_score) tuples
        """
        top_k = top_k or settings.top_k_results
        
        if self.index.ntotal == 0:
            logger.warning("Vector database is empty")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            min(top_k, self.index.ntotal)
        )
        
        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid index
                results.append((self.faqs[idx], float(score)))
        
        logger.info(f"Found {len(results)} results for query")
        return results
    
    def save(self, path: Path = None):
        """
        Save the vector database to disk.
        
        Args:
            path: Save path (uses default if not provided)
        """
        save_path = path or self.db_path
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = save_path / f"{settings.index_name}.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save FAQs
        faqs_path = save_path / "faqs.pkl"
        with open(faqs_path, 'wb') as f:
            pickle.dump(self.faqs, f)
        
        # Save metadata
        metadata = {
            'dimension': self.dimension,
            'total_faqs': len(self.faqs),
            'index_type': 'IndexFlatIP'
        }
        metadata_path = save_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved vector database to {save_path}")
    
    def load(self, path: Path = None):
        """
        Load the vector database from disk.
        
        Args:
            path: Load path (uses default if not provided)
        """
        load_path = path or self.db_path
        
        if not load_path.exists():
            logger.warning(f"Database path does not exist: {load_path}")
            return
        
        # Load FAISS index
        index_path = load_path / f"{settings.index_name}.index"
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
        
        # Load FAQs
        faqs_path = load_path / "faqs.pkl"
        if faqs_path.exists():
            with open(faqs_path, 'rb') as f:
                self.faqs = pickle.load(f)
        
        logger.info(f"Loaded vector database from {load_path} ({len(self.faqs)} FAQs)")
    
    def get_total_faqs(self) -> int:
        """Get the total number of FAQs in the database."""
        return len(self.faqs)
    
    def clear(self):
        """Clear all FAQs and reset the index."""
        self._initialize_index()
        self.faqs = []
        logger.info("Cleared vector database")


# Global vector database instance
_vector_db = None


def get_vector_db() -> VectorDatabase:
    """
    Get or create the global vector database instance.
    
    Returns:
        VectorDatabase instance
    """
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDatabase()
        # Try to load existing database
        _vector_db.load()
    return _vector_db
