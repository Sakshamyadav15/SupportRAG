"""
Test async vs sync query performance
Demonstrates speed improvements from async endpoints and FAISS IVF optimization
"""
import asyncio
import time
from src.core.dual_rag_pipeline import DualStoreRAGPipeline

def test_sync_queries():
    """Test synchronous query performance"""
    print("\n" + "="*60)
    print("🔄 SYNC QUERY PERFORMANCE TEST")
    print("="*60)
    
    pipeline = DualStoreRAGPipeline()
    pipeline.load_vector_stores()  # Load saved vector stores
    
    test_queries = [
        "How do I track my order?",
        "I want to cancel my subscription",
        "My payment was declined",
        "How do I reset my password?",
        "Where is my refund?"
    ]
    
    start = time.time()
    
    for i, query in enumerate(test_queries, 1):
        q_start = time.time()
        result = pipeline.query(query, top_k=3)
        q_time = (time.time() - q_start) * 1000
        
        print(f"\n{i}. Query: {query}")
        print(f"   Source: {result['source']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Latency: {q_time:.0f}ms")
    
    total_time = (time.time() - start) * 1000
    avg_time = total_time / len(test_queries)
    
    print(f"\n{'─'*60}")
    print(f"Total Time: {total_time:.0f}ms")
    print(f"Average Latency: {avg_time:.0f}ms")
    print(f"Queries/sec: {1000/avg_time:.2f}")
    
    return avg_time

async def test_async_queries():
    """Test asynchronous query performance"""
    print("\n" + "="*60)
    print("⚡ ASYNC QUERY PERFORMANCE TEST")
    print("="*60)
    
    pipeline = DualStoreRAGPipeline()
    pipeline.load_vector_stores()  # Load saved vector stores
    
    test_queries = [
        "How do I track my order?",
        "I want to cancel my subscription",
        "My payment was declined",
        "How do I reset my password?",
        "Where is my refund?"
    ]
    
    start = time.time()
    
    # Sequential async queries
    for i, query in enumerate(test_queries, 1):
        q_start = time.time()
        result = await pipeline.aquery(query, top_k=3)
        q_time = (time.time() - q_start) * 1000
        
        print(f"\n{i}. Query: {query}")
        print(f"   Source: {result['source']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Latency: {q_time:.0f}ms")
    
    total_time = (time.time() - start) * 1000
    avg_time = total_time / len(test_queries)
    
    print(f"\n{'─'*60}")
    print(f"Total Time: {total_time:.0f}ms")
    print(f"Average Latency: {avg_time:.0f}ms")
    print(f"Queries/sec: {1000/avg_time:.2f}")
    
    return avg_time

async def test_parallel_async_queries():
    """Test parallel async query performance"""
    print("\n" + "="*60)
    print("🚀 PARALLEL ASYNC QUERY PERFORMANCE TEST")
    print("="*60)
    
    pipeline = DualStoreRAGPipeline()
    pipeline.load_vector_stores()  # Load saved vector stores
    
    test_queries = [
        "How do I track my order?",
        "I want to cancel my subscription",
        "My payment was declined",
        "How do I reset my password?",
        "Where is my refund?"
    ]
    
    start = time.time()
    
    # Run all queries in parallel
    tasks = [pipeline.aquery(query, top_k=3) for query in test_queries]
    results = await asyncio.gather(*tasks)
    
    total_time = (time.time() - start) * 1000
    
    for i, (query, result) in enumerate(zip(test_queries, results), 1):
        print(f"\n{i}. Query: {query}")
        print(f"   Source: {result['source']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Latency: {result['latency_ms']:.0f}ms")
    
    avg_time = total_time / len(test_queries)
    
    print(f"\n{'─'*60}")
    print(f"Total Time: {total_time:.0f}ms (All 5 queries in parallel!)")
    print(f"Average Latency per Query: {avg_time:.0f}ms")
    print(f"Effective Throughput: {1000/avg_time:.2f} queries/sec")
    
    return avg_time, total_time

def main():
    """Run all performance tests"""
    print("\n" + "🎯 "+"="*58)
    print("   RAG PERFORMANCE BENCHMARK")
    print("   Dual Vector Stores: 10,580 FAQs + 5,000 Tickets")
    print("   FAISS Optimization: IVF with 205/141 clusters")
    print("   "+"="*58)
    
    # Test 1: Sync queries
    sync_avg = test_sync_queries()
    
    # Test 2: Async queries (sequential)
    async_avg = asyncio.run(test_async_queries())
    
    # Test 3: Async queries (parallel)
    parallel_avg, parallel_total = asyncio.run(test_parallel_async_queries())
    
    # Summary
    print("\n" + "🏆 "+"="*58)
    print("   PERFORMANCE SUMMARY")
    print("   "+"="*58)
    print(f"\n   Sync Query (baseline):        {sync_avg:.0f}ms avg")
    print(f"   Async Query (sequential):     {async_avg:.0f}ms avg")
    print(f"   Async Query (parallel):       {parallel_total:.0f}ms total for 5 queries")
    print(f"                                  ({parallel_avg:.0f}ms per query)")
    
    sync_improvement = ((sync_avg - async_avg) / sync_avg) * 100
    parallel_speedup = (sync_avg * 5) / parallel_total
    
    print(f"\n   📊 Improvements:")
    print(f"   • Async vs Sync: {sync_improvement:.1f}% faster")
    print(f"   • Parallel Speedup: {parallel_speedup:.1f}x")
    print(f"   • Target Latency (<300ms): {'✅ ACHIEVED' if async_avg < 300 else '❌ NOT YET'}")
    
    print("\n   " + "="*58 + "\n")

if __name__ == "__main__":
    main()
