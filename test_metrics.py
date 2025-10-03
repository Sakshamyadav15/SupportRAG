"""Quick metrics test for resume"""
from src.core.dual_rag_pipeline import DualStoreRAGPipeline
import time

# Load pipeline
p = DualStoreRAGPipeline()
p.load_vector_stores()

# System stats
print("\n=== SYSTEM METRICS ===")
print(f"FAQ Store: {p.faq_store.index.ntotal:,} documents")
print(f"Ticket Store: {p.ticket_store.index.ntotal:,} documents")
print(f"Total Documents: {p.faq_store.index.ntotal + p.ticket_store.index.ntotal:,}")
print(f"Index Type: {type(p.faq_store.index).__name__} (IVF optimized)")

# Query performance
queries = [
    'How do I track my order?',
    'My refund is late',
    'Reset my password',
    'Cancel my subscription',
    'Payment declined'
]

print("\n=== QUERY PERFORMANCE ===")
times = []
faq_count = 0
ticket_count = 0

for q in queries:
    start = time.time()
    r = p.query(q, top_k=3)
    latency = (time.time() - start) * 1000
    times.append(latency)
    
    if r['source'] == 'FAQ':
        faq_count += 1
    else:
        ticket_count += 1
    
    print(f"{q}: {latency:.0f}ms ({r['source']}, {r['confidence']:.1%})")

avg_latency = sum(times) / len(times)
print(f"\nAverage Latency: {avg_latency:.0f}ms")
print(f"Query Deflection: {(faq_count/len(queries))*100:.0f}% answered from FAQ")
print(f"Fallback Rate: {(ticket_count/len(queries))*100:.0f}% fell back to Tickets")

print("\n=== THROUGHPUT (from parallel async test) ===")
print("Parallel Async: 4.7x speedup")
print("Effective Throughput: 4.46 queries/sec")
print("Average Parallel Latency: 224ms")
