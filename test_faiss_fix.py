"""Test: try setting nprobe and searching, or rebuild index"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import faiss
import numpy as np

print("Loading FAQ index...")
index = faiss.read_index(os.path.join("data", "vector_stores", "faq_store", "index.faiss"))
print(f"Index type: {type(index).__name__}, dim={index.d}, ntotal={index.ntotal}")

# IVF index needs nprobe set
print(f"nprobe = {index.nprobe}")
index.nprobe = 5
print(f"Set nprobe = {index.nprobe}")

# Try search with nprobe set
print("\nTrying search with nprobe=5...")
try:
    query = np.random.rand(1, index.d).astype('float32')
    D, I = index.search(query, 3)
    print(f"SUCCESS! D={D}, I={I}")
except Exception as e:
    print(f"Still crashes: {e}")
    
    # Try converting IVF to flat
    print("\nTrying to extract all vectors and create flat index...")
    try:
        # Reconstruct all vectors
        vectors = index.reconstruct_n(0, index.ntotal)
        print(f"Reconstructed {vectors.shape} vectors")
        
        # Create simple flat index
        flat_index = faiss.IndexFlatL2(index.d)
        flat_index.add(vectors)
        print(f"Created flat index with {flat_index.ntotal} vectors")
        
        # Search flat index
        D, I = flat_index.search(query, 3)
        print(f"Flat search SUCCESS! D={D}, I={I}")
    except Exception as e2:
        print(f"Reconstruct also failed: {e2}")

print("\nDone!")
