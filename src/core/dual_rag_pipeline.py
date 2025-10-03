"""
Enhanced RAG Pipeline with Dual Vector Stores (FAQ + Tickets)
Using LangChain + FAISS with fallback retrieval logic
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import pandas as pd
import faiss
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS as LangChainFAISS
from langchain.docstore.document import Document
import google.generativeai as genai

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Custom Embeddings Wrapper for LangChain
class SentenceTransformerEmbeddings(Embeddings):
    """Wrapper for sentence-transformers to use with LangChain"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"Loaded embedding model: {model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        embedding = self.model.encode([text], convert_to_numpy=True)[0]
        return embedding.tolist()


# Simpler non-Pydantic Gemini wrapper
class GeminiLLM:
    """Simple Gemini LLM wrapper (non-LangChain LLM for compatibility)"""
    
    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini LLM: {self.model_name}")
    
    def _call(self, prompt: str) -> str:
        """Call Gemini API"""
        try:
            generation_config = {
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens,
            }
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            raise


class DualStoreRAGPipeline:
    """
    Enhanced RAG Pipeline with dual vector stores:
    - FAQ Store: support_faqs.csv + HuggingFace dataset
    - Ticket Store: support_tickets.csv
    
    Implements fallback logic and metadata tracking
    """
    
    def __init__(self):
        self.embeddings = SentenceTransformerEmbeddings()
        self.llm = GeminiLLM()
        
        self.faq_store: Optional[LangChainFAISS] = None
        self.ticket_store: Optional[LangChainFAISS] = None
        
        self.faq_threshold = 0.65  # Similarity threshold for FAQ
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        logger.info("Initialized DualStoreRAGPipeline")
    
    def load_support_faqs(self) -> List[Document]:
        """Load FAQ documents from local CSV"""
        csv_path = self.data_dir / "support_faqs.csv"
        
        if not csv_path.exists():
            logger.warning(f"FAQ file not found: {csv_path}")
            return []
        
        df = pd.read_csv(csv_path)
        documents = []
        
        for _, row in df.iterrows():
            doc = Document(
                page_content=f"Question: {row['question']}\nAnswer: {row['answer']}",
                metadata={
                    "source": "FAQ",
                    "question": row['question'],
                    "answer": row['answer'],
                    "category": "General"
                }
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} FAQs from CSV")
        return documents
    
    def load_huggingface_faqs(self, max_records: int = 5000) -> List[Document]:
        """Load FAQ documents from HuggingFace dataset"""
        try:
            # Try multiple datasets in order of preference
            datasets_to_try = [
                ("bitext/Bitext-customer-support-llm-chatbot-training-dataset", "instruction", "response"),
                ("MakTek/Customer_support_faqs_dataset", "question", "answer"),
            ]
            
            for dataset_name, question_field, answer_field in datasets_to_try:
                try:
                    logger.info(f"Loading HuggingFace dataset: {dataset_name}")
                    ds = load_dataset(dataset_name)
                    
                    documents = []
                    # Assuming the dataset has 'train' split
                    data = ds['train'] if 'train' in ds else ds
                    
                    # Limit to max_records for performance
                    total_records = len(data)
                    records_to_load = min(max_records, total_records)
                    logger.info(f"Loading {records_to_load} of {total_records} records from HuggingFace")
                    
                    for idx, item in enumerate(data):
                        # Stop if we've reached max_records
                        if idx >= records_to_load:
                            break
                        
                        # Progress indicator every 1000 records
                        if (idx + 1) % 1000 == 0:
                            logger.info(f"Processed {idx + 1}/{records_to_load} HuggingFace records...")
                        
                        # Extract question and answer based on dataset structure
                        question = item.get(question_field, "")
                        answer = item.get(answer_field, "")
                        
                        # Skip if empty
                        if not question or not answer:
                            continue
                        
                        doc = Document(
                            page_content=f"Question: {question}\nAnswer: {answer}",
                            metadata={
                                "source": "FAQ",
                                "question": question,
                                "answer": answer,
                                "category": item.get('category', item.get('intent', 'General')),
                                "origin": "HuggingFace"
                            }
                        )
                        documents.append(doc)
                    
                    logger.info(f"Loaded {len(documents)} FAQs from HuggingFace ({dataset_name})")
                    return documents
                
                except Exception as e:
                    logger.warning(f"Failed to load {dataset_name}: {e}")
                    continue
            
            logger.error("All HuggingFace datasets failed to load")
            return []
        
        except Exception as e:
            logger.error(f"Error loading HuggingFace dataset: {e}")
            return []
    
    def load_support_tickets(self) -> List[Document]:
        """Load support ticket documents from local CSV"""
        csv_path = self.data_dir / "support_tickets.csv"
        
        if not csv_path.exists():
            logger.warning(f"Tickets file not found: {csv_path}")
            return []
        
        df = pd.read_csv(csv_path)
        documents = []
        
        for _, row in df.iterrows():
            doc = Document(
                page_content=f"User Question: {row['user_question']}\nAgent Response: {row['agent_response']}",
                metadata={
                    "source": "Ticket",
                    "user_question": row['user_question'],
                    "agent_response": row['agent_response'],
                    "resolution_status": row['resolution_status'],
                    "category": row['category']
                }
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} support tickets from CSV")
        return documents
    
    def build_vector_stores(self):
        """Build both FAQ and Ticket vector stores"""
        logger.info("Building vector stores...")
        
        # Build FAQ Store
        faq_docs = self.load_support_faqs()
        hf_docs = self.load_huggingface_faqs()
        all_faq_docs = faq_docs + hf_docs
        
        if all_faq_docs:
            self.faq_store = LangChainFAISS.from_documents(
                all_faq_docs,
                self.embeddings
            )
            logger.info(f"FAQ store built with {len(all_faq_docs)} documents")
        else:
            logger.warning("No FAQ documents loaded")
        
        # Build Ticket Store
        ticket_docs = self.load_support_tickets()
        
        if ticket_docs:
            self.ticket_store = LangChainFAISS.from_documents(
                ticket_docs,
                self.embeddings
            )
            logger.info(f"Ticket store built with {len(ticket_docs)} documents")
        else:
            logger.warning("No ticket documents loaded")
        
        logger.info("Vector stores built successfully")
    
    def save_vector_stores(self):
        """Save vector stores to disk"""
        store_dir = self.data_dir / "vector_stores"
        store_dir.mkdir(exist_ok=True)
        
        if self.faq_store:
            faq_path = str(store_dir / "faq_store")
            self.faq_store.save_local(faq_path)
            logger.info(f"FAQ store saved to {faq_path}")
        
        if self.ticket_store:
            ticket_path = str(store_dir / "ticket_store")
            self.ticket_store.save_local(ticket_path)
            logger.info(f"Ticket store saved to {ticket_path}")
    
    def load_vector_stores(self):
        """Load vector stores from disk"""
        store_dir = self.data_dir / "vector_stores"
        
        faq_path = store_dir / "faq_store"
        ticket_path = store_dir / "ticket_store"
        
        if faq_path.exists():
            self.faq_store = LangChainFAISS.load_local(
                str(faq_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("FAQ store loaded from disk")
        
        if ticket_path.exists():
            self.ticket_store = LangChainFAISS.load_local(
                str(ticket_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Ticket store loaded from disk")
    
    def retrieve_with_scores(
        self,
        query: str,
        store_type: str = "faq",
        k: int = 3
    ) -> Tuple[List[Document], List[float]]:
        """Retrieve documents with similarity scores"""
        store = self.faq_store if store_type == "faq" else self.ticket_store
        
        if not store:
            logger.warning(f"{store_type.upper()} store not initialized")
            return [], []
        
        # Get documents with scores
        docs_and_scores = store.similarity_search_with_score(query, k=k)
        
        # Separate documents and scores
        docs = [doc for doc, _ in docs_and_scores]
        scores = [float(score) for _, score in docs_and_scores]
        
        # Convert FAISS L2 distance to similarity percentage
        # FAISS returns L2 distance where lower is better
        # Typical L2 distances for normalized vectors range from 0 (identical) to 2 (opposite)
        # Convert to similarity: similarity = 1 / (1 + distance)
        # This maps: 0 distance -> 1.0 (100%), 1 distance -> 0.5 (50%), 2 distance -> 0.33 (33%)
        similarities = [1.0 / (1.0 + score) for score in scores]
        
        return docs, similarities
    
    def query(
        self,
        question: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Execute query with fallback logic:
        1. Search FAQ store
        2. If max similarity < threshold, fallback to Ticket store
        3. Generate answer with context
        4. Return answer + metadata
        """
        start_time = datetime.now()
        
        # Step 1: Search FAQ store
        faq_docs, faq_similarities = self.retrieve_with_scores(
            question,
            store_type="faq",
            k=top_k
        )
        
        # Determine source based on similarity threshold
        if faq_similarities and faq_similarities[0] >= self.faq_threshold:
            # Use FAQ
            chosen_docs = faq_docs
            chosen_similarities = faq_similarities
            source_type = "FAQ"
            logger.info(f"Using FAQ store (similarity: {faq_similarities[0]:.3f})")
        else:
            # Fallback to Ticket store
            ticket_docs, ticket_similarities = self.retrieve_with_scores(
                question,
                store_type="ticket",
                k=top_k
            )
            chosen_docs = ticket_docs
            chosen_similarities = ticket_similarities
            source_type = "Ticket"
            logger.info(f"Fallback to Ticket store (FAQ similarity: {faq_similarities[0] if faq_similarities else 0:.3f})")
        
        if not chosen_docs:
            return {
                "answer": "I apologize, but I couldn't find relevant information to answer your question. Please contact our support team for assistance.",
                "source": "None",
                "confidence": 0.0,
                "citations": [],
                "latency_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        
        # Build context from retrieved documents
        context_parts = []
        citations = []
        
        for i, (doc, similarity) in enumerate(zip(chosen_docs, chosen_similarities)):
            context_parts.append(doc.page_content)
            
            citation = {
                "rank": i + 1,
                "content": doc.page_content[:200] + "...",
                "similarity": similarity,
                "source": doc.metadata.get("source", "Unknown"),
                "category": doc.metadata.get("category", "General")
            }
            
            # Add ticket-specific metadata
            if source_type == "Ticket":
                citation["resolution_status"] = doc.metadata.get("resolution_status", "unknown")
            
            citations.append(citation)
        
        context = "\n\n".join(context_parts)
        
        # Create prompt template
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
        
        # Generate answer
        prompt = prompt_template.format(context=context, question=question)
        
        try:
            answer = self.llm._call(prompt)
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            answer = f"Based on the available information: {context[:300]}..."
        
        # Calculate latency
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build response
        response = {
            "answer": answer,
            "source": source_type,
            "confidence": chosen_similarities[0] if chosen_similarities else 0.0,
            "citations": citations,
            "latency_ms": latency_ms,
            "query": question,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log query
        self._log_query(response)
        
        logger.info(f"Query completed in {latency_ms:.2f}ms from {source_type} store")
        
        return response
    
    def _log_query(self, response: Dict[str, Any]):
        """Log query details to JSON file"""
        log_file = self.logs_dir / "query_logs.jsonl"
        
        log_entry = {
            "timestamp": response["timestamp"],
            "query": response["query"],
            "source": response["source"],
            "confidence": response["confidence"],
            "latency_ms": response["latency_ms"],
            "num_citations": len(response["citations"])
        }
        
        # Append to JSONL file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")


# Global instance
_pipeline: Optional[DualStoreRAGPipeline] = None


def get_dual_rag_pipeline() -> DualStoreRAGPipeline:
    """Get or create the dual RAG pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = DualStoreRAGPipeline()
    return _pipeline


if __name__ == "__main__":
    # Test the pipeline
    pipeline = DualStoreRAGPipeline()
    
    # Build stores
    pipeline.build_vector_stores()
    pipeline.save_vector_stores()
    
    # Test query
    result = pipeline.query("My refund hasn't arrived in 12 days")
    
    print("\n" + "="*60)
    print("QUERY RESULT")
    print("="*60)
    print(f"Question: {result['query']}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSource: {result['source']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Latency: {result['latency_ms']:.2f}ms")
    print(f"\nCitations ({len(result['citations'])}):")
    for citation in result['citations']:
        print(f"  {citation['rank']}. [{citation['source']}] {citation['category']} - {citation['similarity']:.2%}")
        if 'resolution_status' in citation:
            print(f"     Status: {citation['resolution_status']}")
