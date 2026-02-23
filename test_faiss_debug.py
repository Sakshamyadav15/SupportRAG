"""Debug FAISS crash - check index integrity and dimensions"""
import sys
import os
import traceback

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("FAISS Debug Script")
print("=" * 60)

# Step 1: Check faiss version and basic import
print("\n[1] Checking faiss-cpu version...")
try:
    import faiss
    print(f"    faiss version: {faiss.__version__ if hasattr(faiss, '__version__') else 'unknown'}")
    print(f"    faiss path: {faiss.__file__}")
except Exception as e:
    print(f"    ERROR: {e}")
    sys.exit(1)

# Step 2: Check numpy version
print("\n[2] Checking numpy...")
import numpy as np
print(f"    numpy version: {np.__version__}")

# Step 3: Try loading FAISS index directly (not through LangChain)
print("\n[3] Loading FAQ FAISS index directly...")
faq_index_path = os.path.join("data", "vector_stores", "faq_store", "index.faiss")
try:
    index = faiss.read_index(faq_index_path)
    print(f"    Index loaded!")
    print(f"    Index type: {type(index)}")
    print(f"    Dimension: {index.d}")
    print(f"    Total vectors: {index.ntotal}")
    print(f"    Is trained: {index.is_trained}")
except Exception as e:
    print(f"    ERROR loading index: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 4: Try a raw FAISS search
print("\n[4] Trying raw FAISS search...")
try:
    # Create a random query vector matching the index dimension
    query_vec = np.random.rand(1, index.d).astype('float32')
    print(f"    Query shape: {query_vec.shape}, dtype: {query_vec.dtype}")
    distances, indices = index.search(query_vec, 3)
    print(f"    Search succeeded!")
    print(f"    Distances: {distances}")
    print(f"    Indices: {indices}")
except Exception as e:
    print(f"    ERROR during raw search: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 5: Try with actual embeddings
print("\n[5] Loading embedding model...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embedding = model.encode(["damaged product"], convert_to_numpy=True)
    print(f"    Embedding shape: {embedding.shape}, dtype: {embedding.dtype}")
    print(f"    Index dimension: {index.d}")
    
    if embedding.shape[1] != index.d:
        print(f"    *** DIMENSION MISMATCH! Embedding={embedding.shape[1]}, Index={index.d} ***")
    else:
        print(f"    Dimensions match!")
except Exception as e:
    print(f"    ERROR: {e}")
    traceback.print_exc()

# Step 6: Try FAISS search with real embedding
print("\n[6] FAISS search with real embedding...")
try:
    query_vec = embedding.astype('float32')
    distances, indices = index.search(query_vec, 3)
    print(f"    Search succeeded!")
    print(f"    Distances: {distances}")
    print(f"    Indices: {indices}")
except Exception as e:
    print(f"    ERROR: {e}")
    traceback.print_exc()

# Step 7: Try loading through LangChain
print("\n[7] Loading via LangChain FAISS...")
try:
    from langchain_community.vectorstores import FAISS as LangChainFAISS
    from langchain.embeddings.base import Embeddings
    
    class SimpleEmbeddings(Embeddings):
        def __init__(self):
            self.model = model
        def embed_documents(self, texts):
            return self.model.encode(texts, convert_to_numpy=True).tolist()
        def embed_query(self, text):
            return self.model.encode([text], convert_to_numpy=True)[0].tolist()
    
    embeddings = SimpleEmbeddings()
    store = LangChainFAISS.load_local(
        os.path.join("data", "vector_stores", "faq_store"),
        embeddings,
        allow_dangerous_deserialization=True
    )
    print(f"    LangChain FAISS store loaded!")
    print(f"    Store type: {type(store)}")
except Exception as e:
    print(f"    ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 8: Try LangChain similarity search
print("\n[8] LangChain similarity_search_with_score...")
try:
    results = store.similarity_search_with_score("damaged product", k=3)
    print(f"    SUCCESS! Got {len(results)} results")
    for doc, score in results:
        print(f"    Score={score:.4f}: {doc.page_content[:80]}...")
except Exception as e:
    print(f"    ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug complete!")
print("=" * 60)
