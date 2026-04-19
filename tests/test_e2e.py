"""Quick end-to-end test"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.dual_rag_pipeline import DualStoreRAGPipeline

print("Init...")
p = DualStoreRAGPipeline()
print("Loading stores...")
p.load_vector_stores()
print("Querying...")
r = p.query("My product arrived damaged")
print(f"\nANSWER: {r['answer'][:500]}")
print(f"\nSOURCE: {r['source']}")
print(f"CONFIDENCE: {r['confidence']:.2%}")
print(f"LATENCY: {r['latency_ms']:.0f}ms")
print("\nSUCCESS!")
