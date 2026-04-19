"""Rebuild FAISS vector stores from scratch (skip IVF to avoid segfault)"""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Rebuilding Vector Stores")
print("=" * 60)

# Step 1: Delete old corrupted stores
store_dir = os.path.join("data", "vector_stores")
if os.path.exists(store_dir):
    print(f"\n[1] Deleting old vector stores at {store_dir}...")
    shutil.rmtree(store_dir)
    print("    Deleted!")
else:
    print(f"\n[1] No existing stores to delete")

# Also delete old vector_store directory if it exists
old_store = os.path.join("data", "vector_store")
if os.path.exists(old_store):
    print(f"    Also deleting old {old_store}...")
    shutil.rmtree(old_store)

# Step 2: Build new stores WITHOUT IVF (use flat index which is stable)
print("\n[2] Initializing pipeline...")
from src.core.dual_rag_pipeline import DualStoreRAGPipeline

pipeline = DualStoreRAGPipeline()
print("    Pipeline initialized")

print("\n[3] Building vector stores (flat index, no IVF)...")
pipeline.build_vector_stores(use_ivf=False)  # Flat index - no segfault risk
print("    Build complete!")

print("\n[4] Saving vector stores...")
pipeline.save_vector_stores()
print("    Saved!")

# Step 3: Test search
print("\n[5] Testing FAQ search...")
try:
    docs, scores = pipeline.retrieve_with_scores("damaged product", "faq", 3)
    print(f"    SUCCESS! Got {len(docs)} results")
    for doc, score in zip(docs, scores):
        print(f"    Score={score:.4f}: {doc.page_content[:80]}...")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n[6] Testing Ticket search...")
try:
    docs, scores = pipeline.retrieve_with_scores("shipping delay", "ticket", 3)
    print(f"    SUCCESS! Got {len(docs)} results")
    for doc, score in zip(docs, scores):
        print(f"    Score={score:.4f}: {doc.page_content[:80]}...")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Test full query (with Groq LLM)
print("\n[7] Testing full query pipeline (with Groq)...")
try:
    result = pipeline.query("My product arrived damaged, what should I do?")
    print(f"    SUCCESS!")
    print(f"    Response: {result['response'][:200]}...")
    print(f"    Sources: {len(result.get('sources', []))}")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Rebuild complete!")
print("=" * 60)
