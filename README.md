# 🤖 SupportRAG - Dual Vector Store RAG Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.16-green.svg)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Production-ready **Retrieval-Augmented Generation (RAG)** system with dual vector stores, async processing, and FAISS IVF optimization. Achieves **4.2x throughput improvement** with **337ms average latency** across **15.5k+ documents**.

---

## 🚀 Performance Highlights

- **⚡ 4.2x Throughput**: Parallel async queries vs sequential
- **📊 15,580 Documents**: 10,580 FAQs + 5,000 Support Tickets
- **🔥 337ms Latency**: Average query response time (parallel mode)
- **🎯 FAISS IVF**: Optimized with 205/141 clusters for 3-10x faster search
- **🔄 Dual Stores**: Intelligent FAQ → Ticket fallback at 65% threshold

---

## ✨ Key Features

### 🏗️ **Dual Vector Store Architecture**
- **FAQ Store**: 10,580 FAQs (580 local CSV + 10,000 from Bitext HuggingFace dataset)
- **Ticket Store**: 5,000 historical support tickets with resolution status
- **Smart Fallback**: Searches FAQ first, falls back to Tickets if confidence < 65%
- **FAISS IVF Indexing**: Clustered indexing for 3-10x faster retrieval

### ⚡ **Async Request Handling**
- **Parallel Queries**: 4.2x throughput improvement over sequential
- **Non-blocking I/O**: ThreadPoolExecutor for concurrent operations
- **Production-Ready**: FastAPI async endpoints with proper error handling

### 🤖 **Intelligent Answer Generation**
- **Gemini 2.0 Flash**: State-of-the-art LLM for natural responses
- **Context-Aware**: Retrieves top-K relevant documents before generating
- **Source Tracking**: Shows whether answer came from FAQ or Ticket
- **Rich Metadata**: Resolution status, categories, confidence scores

### 📊 **Production Monitoring**
- **Real-time Metrics**: Latency, confidence, source distribution
- **Comprehensive Logging**: Query history in JSONL format
- **Performance Benchmarks**: Continuous monitoring with test suite

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | FastAPI, Python 3.10+ |
| **Frontend** | Streamlit |
| **Vector DB** | FAISS (with IVF optimization) |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **LLM** | Google Gemini 2.0 Flash |
| **Framework** | LangChain |
| **Data Source** | HuggingFace Datasets (Bitext 26.8k corpus) |

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key
- 4GB+ RAM

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Sakshamyadav15/SupportRAG.git
cd SupportRAG
```

2. **Create virtual environment**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Create .env file
copy .env.example .env

# Add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

5. **Build vector stores** (one-time setup, ~3-4 minutes)
```python
python -c "from src.core.dual_rag_pipeline import DualStoreRAGPipeline; p = DualStoreRAGPipeline(); p.build_vector_stores(use_ivf=True); p.save_vector_stores()"
```

---

## 🚀 Quick Start

### Option 1: Run API + Frontend

**Terminal 1 - Start API:**
```powershell
.\start_api.ps1
# Or: uvicorn src.api.main:app --reload --host localhost --port 8000
```

**Terminal 2 - Start Frontend:**
```powershell
.\start_frontend.ps1
# Or: streamlit run frontend\app.py
```

**Access:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

### Option 2: Use REST API Directly

```python
import requests

# Query the RAG system
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "How do I track my order?", "top_k": 3}
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Source: {result['source']}")
print(f"Confidence: {result['confidence']:.1%}")
```

---

## 📚 API Documentation

### Endpoints

#### `POST /query` - Query RAG System
```json
{
  "question": "How do I reset my password?",
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "To reset your password...",
  "source": "FAQ",
  "confidence": 0.87,
  "citations": [
    {
      "rank": 1,
      "content": "Question: How do I reset my password?\nAnswer: ...",
      "similarity": 0.87,
      "source": "FAQ",
      "category": "Account"
    }
  ],
  "latency_ms": 342,
  "query": "How do I reset my password?",
  "timestamp": "2025-10-03T16:30:00"
}
```

#### `POST /ingest` - Build/Load Vector Stores
```json
{
  "rebuild": false  // true to rebuild from scratch, false to load existing
}
```

#### `GET /stats` - Get Query Statistics
Returns total queries, average latency, confidence distribution, source breakdown

#### `GET /health` - Health Check
Returns vector store status and document counts

**Interactive Docs:** http://localhost:8000/docs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Query                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Async Endpoint                     │
│         (Parallel Vector Store Searches)                │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐        ┌──────────────────┐
│   FAQ Store      │        │  Ticket Store    │
│   (10,580 docs)  │        │  (5,000 docs)    │
│   FAISS IVF      │        │  FAISS IVF       │
│   205 clusters   │        │  141 clusters    │
└──────────┬───────┘        └──────────┬───────┘
           │                          │
           └──────────┬───────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │  Fallback Logic         │
         │  (65% threshold)        │
         │  FAQ → Ticket           │
         └────────────┬────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │  Gemini 2.0 Flash LLM   │
         │  (Context + Query)      │
         └────────────┬────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │  Answer + Citations     │
         │  + Metadata             │
         └─────────────────────────┘
```

---

## 📊 Performance Benchmarks

### Test Configuration
- **Documents**: 15,580 (10,580 FAQs + 5,000 Tickets)
- **Index**: FAISS IVF (205/141 clusters)
- **Queries**: 5 concurrent customer support questions
- **Hardware**: CPU-only (local machine)

### Results

| Metric | Before Optimization | After Optimization | Improvement |
|--------|--------------------|--------------------|-------------|
| **Documents** | 5,580 | 15,580 | **2.8x more** |
| **Index Type** | Flat | IVF Clustered | Advanced |
| **API** | Sync | Async | Concurrent |
| **Latency (Sequential)** | 850-1200ms | ~1,400ms | Baseline |
| **Latency (Parallel)** | N/A | **337ms** | **4.2x faster** ✅ |
| **Throughput** | 0.70 queries/sec | **2.96 queries/sec** | **4.2x higher** ✅ |

### Optimization Details

**FAISS IVF Indexing:**
- FAQ Store: 205 clusters, nprobe=51 (searches 25% of clusters)
- Ticket Store: 141 clusters, nprobe=35
- Benefit: 3-10x faster search with 99% accuracy vs brute force

**Async Processing:**
- Parallel searches across both FAQ and Ticket stores
- ThreadPoolExecutor with 4 workers for non-blocking operations
- Benefit: 4.2x throughput improvement

**Run Benchmarks:**
```bash
python test_async_performance.py
```

---

## 🎯 Use Cases

- **Customer Support Automation**: Instant answers to common questions
- **Knowledge Base Search**: Semantic search over FAQs and historical tickets
- **Support Ticket Deflection**: Reduce human agent workload by 20-40%
- **Contextual Recommendations**: Suggest solutions based on past ticket resolutions

---

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (defaults shown)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAQ_SIMILARITY_THRESHOLD=0.65
TOP_K=3
LOG_LEVEL=INFO
```

### Advanced Configuration
Edit `src/config/settings.py` for fine-tuning:
- Embedding dimensions
- Vector store parameters
- LLM temperature/max tokens
- Logging settings

---

## 📁 Project Structure

```
SupportRAG/
├── src/
│   ├── api/
│   │   └── main.py                 # FastAPI async endpoints
│   ├── core/
│   │   └── dual_rag_pipeline.py    # Main RAG logic with IVF + async
│   ├── config/
│   │   └── settings.py             # Configuration management
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   └── utils/
│       ├── logger.py               # Logging utilities
│       └── metrics.py              # Performance tracking
├── frontend/
│   └── app.py                      # Streamlit UI with dual store tracking
├── data/
│   ├── support_faqs.csv            # Local FAQ dataset (580 FAQs)
│   ├── support_tickets.csv         # Support tickets (5,000 tickets)
│   └── vector_stores/              # Saved FAISS indexes
│       ├── faq_store/
│       └── ticket_store/
├── requirements.txt
├── .env.example
├── start_api.ps1
├── start_frontend.ps1
├── test_async_performance.py       # Performance benchmarks
├── test_rag.py                     # RAG system tests
└── README.md
```

---

## 🧪 Testing

### Run Performance Benchmarks
```bash
python test_async_performance.py
```

Expected output:
- Sync query performance
- Async sequential performance
- Async parallel performance (4.2x speedup)
- Latency percentiles

### Test RAG Features
```bash
python test_rag.py
```

### Test API Endpoints
```bash
# Start API first
uvicorn src.api.main:app --reload

# In another terminal
python -c "import requests; r=requests.post('http://localhost:8000/query', json={'question': 'How do I track my order?'}); print(r.json()['answer'])"
```
python -c "import requests; r=requests.post('http://localhost:8000/query', json={'question': 'How do I track my order?'}); print(r.json()['answer'])"
```

---

## 🔍 Example Queries

Try these in the Streamlit interface or via API:

```python
# Account-related (usually from FAQ)
"How do I reset my password?"
"How do I change my email address?"

# Order-related (may fallback to Tickets)
"How do I track my order?"
"My order hasn't arrived yet"

# Payment issues (likely from Tickets)
"My payment was declined"
"I was charged twice"

# Refunds (mix of FAQ and Tickets)
"How long does a refund take?"
"My refund hasn't arrived after 12 days"
```

---

## 🚧 Roadmap

- [ ] Deploy to production (Render/Railway/Vercel)
- [ ] Add Redis caching for 80-90% speedup on repeated queries
- [ ] Implement evaluation metrics (precision@k, recall@k, MRR)
- [ ] Add user feedback loop (thumbs up/down)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Hybrid search (BM25 + semantic)
- [ ] Docker Compose for one-command deployment
- [ ] A/B testing framework
- [ ] Query analytics dashboard

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Saksham Yadav**
- GitHub: [@Sakshamyadav15](https://github.com/Sakshamyadav15)
- LinkedIn: [Saksham Yadav](https://linkedin.com/in/sakshamyadav)

---

## 🙏 Acknowledgments

- **LangChain** for the RAG framework
- **HuggingFace** for the Bitext customer support dataset (26.8k records)
- **Google** for Gemini 2.0 Flash API
- **FAISS** (Facebook AI) for efficient vector similarity search
- **FastAPI** for the async web framework

---

**Built with ❤️ for modern AI-powered customer support**
