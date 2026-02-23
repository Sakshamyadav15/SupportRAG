"""Quick debug script to test pipeline step by step"""
import os, sys
os.chdir("c:/Saksham/Work/Projects/SupportRAG")
sys.stdout.reconfigure(line_buffering=True)

from src.core.dual_rag_pipeline import get_dual_rag_pipeline

p = get_dual_rag_pipeline()
p.load_vector_stores()

print("Step 1: retrieve FAQ", flush=True)
docs, sims = p.retrieve_with_scores("damaged product", "faq", 3)
print(f"  Got {len(docs)} docs, top sim: {sims[0]:.3f}", flush=True)

print("Step 2: retrieve Tickets", flush=True)
docs2, sims2 = p.retrieve_with_scores("damaged product", "ticket", 3)
print(f"  Got {len(docs2)} docs, top sim: {sims2[0]:.3f}", flush=True)

print("Step 3: LLM call", flush=True)
ans = p.llm._call("Say OK")
print(f"  LLM: {ans}", flush=True)

print("Step 4: full query()", flush=True)
r = p.query("The product I received is damaged")
print(f"  Source: {r['source']}, Confidence: {r['confidence']:.2f}", flush=True)
print(f"  Answer: {r['answer'][:150]}...", flush=True)

print("\nStep 5: async aquery()", flush=True)
import asyncio
r2 = asyncio.run(p.aquery("The product I received is damaged"))
print(f"  Source: {r2['source']}, Confidence: {r2['confidence']:.2f}", flush=True)
print(f"  Answer: {r2['answer'][:150]}...", flush=True)

print("\nALL TESTS PASSED", flush=True)
