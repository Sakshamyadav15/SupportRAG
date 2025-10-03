"""
Script to initialize the vector database with FAQ data.
Loads FAQs from CSV and creates FAISS index.
"""
import sys
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.vectordb import get_vector_db
from src.models.schemas import FAQItem
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_faqs_from_csv(csv_path: str) -> list:
    """Load FAQs from CSV file."""
    logger.info(f"Loading FAQs from {csv_path}")
    
    df = pd.read_csv(csv_path)
    faqs = []
    
    for _, row in df.iterrows():
        faq = FAQItem(
            id=row.get('id'),
            question=row['question'],
            answer=row['answer'],
            category=row.get('category', 'general')
        )
        faqs.append(faq)
    
    logger.info(f"Loaded {len(faqs)} FAQs from CSV")
    return faqs


def main():
    """Initialize vector database with FAQ data."""
    logger.info("=== Initializing Vector Database ===")
    
    # Get vector database instance
    vector_db = get_vector_db()
    
    # Clear existing data
    logger.info("Clearing existing vector database...")
    vector_db.clear()
    
    # Load FAQs from CSV
    csv_path = settings.faq_data_path
    if not Path(csv_path).exists():
        logger.error(f"FAQ data file not found: {csv_path}")
        return
    
    faqs = load_faqs_from_csv(csv_path)
    
    # Add FAQs to vector database
    logger.info("Adding FAQs to vector database...")
    faq_ids = vector_db.add_faqs_batch(faqs)
    logger.info(f"Successfully added {len(faq_ids)} FAQs")
    
    # Save vector database
    logger.info("Saving vector database...")
    vector_db.save()
    logger.info(f"Vector database saved to {settings.vector_db_path}")
    
    # Test retrieval
    logger.info("\n=== Testing Retrieval ===")
    test_query = "How do I reset my password?"
    logger.info(f"Test query: {test_query}")
    
    results = vector_db.search(test_query, top_k=3)
    logger.info(f"Found {len(results)} results:")
    
    for i, (faq, score) in enumerate(results, 1):
        logger.info(f"\n{i}. Score: {score:.4f}")
        logger.info(f"   Q: {faq.question}")
        logger.info(f"   A: {faq.answer[:100]}...")
    
    logger.info("\n=== Initialization Complete ===")
    logger.info(f"Total FAQs in database: {vector_db.get_total_faqs()}")


if __name__ == "__main__":
    main()
