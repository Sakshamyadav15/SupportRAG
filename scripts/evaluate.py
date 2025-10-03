"""
Evaluation script for testing RAG system accuracy.
Compares retrieval results against ground truth test set.
"""
import sys
import pandas as pd
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.rag_pipeline import get_rag_pipeline
from src.models.schemas import QueryRequest
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_test_queries(csv_path: str) -> pd.DataFrame:
    """Load test queries from CSV."""
    return pd.read_csv(csv_path)


def evaluate_retrieval_accuracy(test_df: pd.DataFrame, top_k: int = 3):
    """
    Evaluate retrieval accuracy against ground truth.
    
    Args:
        test_df: DataFrame with test queries and ground truth
        top_k: Number of results to retrieve
    """
    rag_pipeline = get_rag_pipeline()
    
    total_queries = len(test_df)
    correct_at_1 = 0
    correct_at_k = 0
    total_latency = 0
    escalations = 0
    
    results = []
    
    logger.info(f"Evaluating {total_queries} test queries...")
    
    for idx, row in test_df.iterrows():
        question = row['question']
        ground_truth_id = row['ground_truth_faq_id']
        
        # Create query request
        request = QueryRequest(question=question, top_k=top_k)
        
        # Get response
        start_time = time.time()
        response = rag_pipeline.query(request)
        latency = (time.time() - start_time) * 1000
        
        total_latency += latency
        
        # Check if escalated
        if response.escalated:
            escalations += 1
        
        # Check accuracy
        retrieved_ids = [c.faq_id for c in response.citations]
        
        if retrieved_ids and retrieved_ids[0] == ground_truth_id:
            correct_at_1 += 1
        
        if ground_truth_id in retrieved_ids:
            correct_at_k += 1
        
        results.append({
            'question': question,
            'ground_truth': ground_truth_id,
            'retrieved_ids': retrieved_ids,
            'top_match': retrieved_ids[0] if retrieved_ids else None,
            'correct_at_1': retrieved_ids[0] == ground_truth_id if retrieved_ids else False,
            'correct_at_k': ground_truth_id in retrieved_ids,
            'confidence': response.confidence_score,
            'escalated': response.escalated,
            'latency_ms': latency
        })
        
        logger.info(f"[{idx+1}/{total_queries}] {question[:50]}... - "
                   f"Correct@1: {results[-1]['correct_at_1']}, "
                   f"Correct@{top_k}: {results[-1]['correct_at_k']}")
    
    # Calculate metrics
    accuracy_at_1 = (correct_at_1 / total_queries) * 100
    accuracy_at_k = (correct_at_k / total_queries) * 100
    avg_latency = total_latency / total_queries
    escalation_rate = (escalations / total_queries) * 100
    
    # Print results
    logger.info("\n" + "="*60)
    logger.info("EVALUATION RESULTS")
    logger.info("="*60)
    logger.info(f"Total Test Queries: {total_queries}")
    logger.info(f"Accuracy@1: {accuracy_at_1:.2f}%")
    logger.info(f"Accuracy@{top_k}: {accuracy_at_k:.2f}%")
    logger.info(f"Average Latency: {avg_latency:.2f}ms")
    logger.info(f"Escalation Rate: {escalation_rate:.2f}%")
    logger.info("="*60)
    
    # Save results
    results_df = pd.DataFrame(results)
    output_path = project_root / "logs" / "evaluation_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    logger.info(f"\nDetailed results saved to: {output_path}")
    
    return {
        'accuracy_at_1': accuracy_at_1,
        'accuracy_at_k': accuracy_at_k,
        'avg_latency': avg_latency,
        'escalation_rate': escalation_rate,
        'results': results_df
    }


def main():
    """Run evaluation."""
    logger.info("=== Starting RAG System Evaluation ===\n")
    
    # Load test queries
    test_path = settings.test_data_path
    if not Path(test_path).exists():
        logger.error(f"Test data file not found: {test_path}")
        return
    
    test_df = load_test_queries(test_path)
    logger.info(f"Loaded {len(test_df)} test queries\n")
    
    # Run evaluation
    results = evaluate_retrieval_accuracy(test_df, top_k=3)
    
    logger.info("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    main()
