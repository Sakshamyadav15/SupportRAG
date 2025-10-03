"""
Embedding service for converting text to vectors.
Supports sentence-transformers and Gemini embeddings.
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Successfully loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array containing the embedding vector
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of shape (len(texts), embedding_dim)
        """
        try:
            batch_size = batch_size or settings.batch_size
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100
            )
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension size
        """
        return self.model.get_sentence_embedding_dimension()
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        return float(np.dot(embedding1, embedding2) / 
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
