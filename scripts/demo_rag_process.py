"""Demo RAG: Show the raw context retrieved before Groq generates the answer"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.dual_rag_pipeline import DualStoreRAGPipeline

print("Initializing RAG pipeline (loading stores)...")
pipeline = DualStoreRAGPipeline()
pipeline.load_vector_stores()

# Example query that needs specific knowledge from the vector store
query = "My product arrived damaged"

print(f"\nExample Query: '{query}'")
print("-" * 60)

# Step 1: Retrieval (What specific info did we find in your local files?)
print("\n[Step 1: Retrieval] Searching local vector stores...")
# Search both stores
faq_docs, faq_scores = pipeline.retrieve_with_scores(query, "faq", 1)
ticket_docs, ticket_scores = pipeline.retrieve_with_scores(query, "ticket", 1)

print(f"   Found in FAQ (similarity {faq_scores[0]:.2f}):")
print(f"   \"{faq_docs[0].page_content[:100]}...\"")

print(f"   Found in Tickets (similarity {ticket_scores[0]:.2f}):")
print(f"   \"{ticket_docs[0].page_content[:100]}...\"")

# Step 2: Augmemtation (Constructing the prompt)
chosen_doc = ticket_docs[0] # Let's say we chose the ticket because score is higher
context = chosen_doc.page_content

prompt_template = """You are a helpful customer support assistant. Use the following context to answer the user's question.

Context:
{context}

User Question: {question}

Instructions:
- Provide a clear, helpful answer based on the context
- If the context comes from a support ticket, acknowledge similar past issues
- Be concise but complete
- If you're not sure, say so

Answer:"""

final_prompt = prompt_template.format(context=context, question=query)

print("\n[Step 2: Augmentation] Constructing the Prompt for Groq...")
print("-" * 60)
print(final_prompt)
print("-" * 60)

# Step 3: Generation (Groq answer)
print("\n[Step 3: Generation] Sending prompt to Groq...")
answer = pipeline.llm._call(final_prompt)
print(f"\nGroq Answer:\n{answer}")
print("-" * 60)
