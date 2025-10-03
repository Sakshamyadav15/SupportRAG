# 🚀 Enhanced RAG Pipeline - Setup & Testing Guide

## 🎯 Overview

You now have an **advanced dual vector store RAG system** with:

### ✨ Key Features
1. **Dual Vector Stores**:
   - FAQ Store: `support_faqs.csv` + HuggingFace dataset
   - Ticket Store: `support_tickets.csv`

2. **Intelligent Fallback Logic**:
   - Query → FAQ store first
   - If similarity < 0.65 → fallback to Ticket store
   - Smart source selection

3. **Rich Metadata**:
   - Source tracking (FAQ vs Ticket)
   - Resolution status for tickets
   - Category classification
   - Confidence scores
   - Citations with similarity scores

4. **LangChain Integration**:
   - Professional RAG pipeline
   - Custom Gemini LLM wrapper
   - Extensible architecture

---

## 📋 Prerequisites

### 1. Install New Dependencies
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Install new packages
pip install langchain==0.1.16
pip install langchain-community==0.0.29
pip install langchain-core==0.1.33
pip install datasets==2.18.0
pip install faiss-cpu==1.8.0
pip install --upgrade google-generativeai
```

### 2. Verify HuggingFace Login
```powershell
# You should already be logged in
huggingface-cli whoami

# If not, login:
huggingface-cli login
```

---

## 🏃 Quick Start

### Option A: Step-by-Step (Recommended First Time)

#### Step 1: Start Enhanced API
```powershell
# Terminal 1
.\start_api_enhanced.ps1
```

Wait for:
```
INFO:     Application startup complete.
```

#### Step 2: Build Vector Stores
```powershell
# In a new terminal or use API
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d "{\"rebuild\": true}"
```

Or use Python:
```powershell
python -c "import requests; r = requests.post('http://localhost:8000/ingest', json={'rebuild': True}); print(r.json())"
```

Expected output:
```json
{
  "status": "success",
  "faq_count": 40,
  "ticket_count": 20,
  "message": "Vector stores built successfully..."
}
```

#### Step 3: Start Enhanced Frontend
```powershell
# Terminal 2
.\start_frontend_enhanced.ps1
```

#### Step 4: Open Browser
```
http://localhost:8501
```

---

### Option B: Quick Test (Command Line)

```powershell
# Test the pipeline directly
python src/core/dual_rag_pipeline.py
```

This will:
1. Build vector stores
2. Save to disk
3. Run a test query
4. Show formatted results

---

## 🧪 Testing the System

### Test 1: FAQ Query (Should use FAQ store)
**Question**: "How do I track my order?"

**Expected**:
- Source: FAQ
- Confidence: >70%
- Quick response
- No resolution status

### Test 2: Ticket Query (Should use Ticket store)
**Question**: "My refund hasn't arrived after 12 days"

**Expected**:
- Source: Ticket
- Confidence: >60%
- Resolution Status: open/closed
- Category: Refunds

### Test 3: Edge Case (Low confidence)
**Question**: "What's the weather today?"

**Expected**:
- Low confidence
- Fallback behavior
- Suggests contacting support

---

## 📁 Project Structure (Updated)

```
SupportRAG/
├── data/
│   ├── support_faqs.csv           # ✅ Local FAQs
│   ├── support_tickets.csv        # ✅ Support tickets
│   └── vector_stores/             # 🆕 Saved FAISS indexes
│       ├── faq_store/
│       └── ticket_store/
├── src/
│   ├── api/
│   │   ├── main.py                # Original API
│   │   └── main_enhanced.py       # 🆕 Dual store API
│   └── core/
│       ├── rag_pipeline.py        # Original pipeline
│       └── dual_rag_pipeline.py   # 🆕 Enhanced pipeline
├── frontend/
│   ├── app.py                     # Original UI
│   └── app_enhanced.py            # 🆕 Enhanced UI
├── logs/
│   └── query_logs.jsonl           # 🆕 Query logging
├── start_api_enhanced.ps1         # 🆕 Start enhanced API
└── start_frontend_enhanced.ps1    # 🆕 Start enhanced frontend
```

---

## 🔍 API Endpoints

### GET /
Welcome message

### GET /health
```json
{
  "status": "healthy",
  "faq_store_loaded": true,
  "ticket_store_loaded": true,
  "faq_threshold": 0.65
}
```

### POST /ingest
Build vector stores

**Request**:
```json
{
  "rebuild": true  // or false to load existing
}
```

**Response**:
```json
{
  "status": "success",
  "faq_count": 40,
  "ticket_count": 20,
  "message": "Vector stores built successfully..."
}
```

### POST /query
Query the RAG system

**Request**:
```json
{
  "question": "My refund hasn't arrived",
  "top_k": 3
}
```

**Response**:
```json
{
  "answer": "Refunds typically take 5-7 business days...",
  "source": "Ticket",
  "confidence": 0.78,
  "citations": [
    {
      "rank": 1,
      "content": "User Question: My refund hasn't arrived...",
      "similarity": 0.78,
      "source": "Ticket",
      "category": "Refunds",
      "resolution_status": "closed"
    }
  ],
  "latency_ms": 1234.56,
  "query": "My refund hasn't arrived",
  "timestamp": "2025-10-03T14:30:00"
}
```

### GET /stats
Get query statistics

**Response**:
```json
{
  "total_queries": 42,
  "avg_latency_ms": 856.23,
  "avg_confidence": 0.7234,
  "source_breakdown": {
    "FAQ": 28,
    "Ticket": 14
  }
}
```

---

## 🎨 UI Features

### Main Chat Interface
- Real-time chat with message history
- Source badges (FAQ/Ticket with color coding)
- Confidence indicators (✅ High, ⚠️ Medium, ❌ Low)
- Latency tracking

### Citation Display
- Expandable citation cards
- Source type and category
- Similarity scores
- Resolution status for tickets
- Truncated content preview

### Sidebar Controls
- **API Health**: Connection status
- **Data Ingestion**: Build/load stores
- **Statistics**: Query metrics
- **Settings**: Top-K slider

### Example Questions
- Pre-configured test questions
- One-click testing
- Clear chat functionality

---

## 📊 Logging & Monitoring

### Query Logs
Location: `logs/query_logs.jsonl`

Format (one JSON per line):
```json
{"timestamp": "2025-10-03T14:30:00", "query": "...", "source": "FAQ", "confidence": 0.85, "latency_ms": 450, "num_citations": 3}
```

### Analysis
```powershell
# Count queries
Get-Content logs/query_logs.jsonl | Measure-Object -Line

# View last 10 queries
Get-Content logs/query_logs.jsonl | Select-Object -Last 10 | ConvertFrom-Json | Format-Table
```

---

## 🔧 Troubleshooting

### Issue: "Vector stores not initialized"
**Solution**:
```powershell
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d "{\"rebuild\": true}"
```

### Issue: "HuggingFace dataset not loading"
**Solution**:
1. Check internet connection
2. Verify HuggingFace login: `huggingface-cli whoami`
3. Try loading manually:
```python
from datasets import load_dataset
ds = load_dataset("MakTek/Customer_support_faqs_dataset")
print(ds)
```

### Issue: "ImportError: No module named langchain"
**Solution**:
```powershell
pip install langchain==0.1.16 langchain-community==0.0.29 langchain-core==0.1.33
```

### Issue: "API returns 500 error"
**Solution**:
1. Check logs in terminal
2. Verify Gemini API key in `.env`
3. Test LLM directly:
```python
from src.core.dual_rag_pipeline import GeminiLLM
llm = GeminiLLM()
print(llm._call("Test: What is 2+2?"))
```

---

## 🚀 Advanced Usage

### Customize Threshold
Edit `src/core/dual_rag_pipeline.py`:
```python
self.faq_threshold = 0.70  # Change from 0.65
```

### Add More Data Sources
Edit `load_huggingface_faqs()` to load additional datasets:
```python
ds2 = load_dataset("another/dataset")
# Process and add to documents
```

### Change Embedding Model
Edit `SentenceTransformerEmbeddings`:
```python
self.model = SentenceTransformer("all-mpnet-base-v2")  # Larger model
```

### Switch to Pinecone
Replace FAISS with Pinecone in `dual_rag_pipeline.py`:
```python
from langchain.vectorstores import Pinecone
# Update build_vector_stores() method
```

---

## 📈 Performance Expectations

| Metric | FAQ Store | Ticket Store |
|--------|-----------|--------------|
| **Build Time** | ~30 seconds | ~5 seconds |
| **Query Latency** | 400-800ms | 400-800ms |
| **Memory Usage** | ~500MB | ~200MB |
| **Accuracy** | 85%+ | 75%+ |

---

## ✅ Testing Checklist

- [ ] API starts successfully
- [ ] Vector stores build without errors
- [ ] FAQ queries return FAQ source
- [ ] Ticket queries return Ticket source
- [ ] Confidence scores displayed correctly
- [ ] Resolution status shown for tickets
- [ ] Categories displayed properly
- [ ] Citations expandable and readable
- [ ] Latency < 1 second
- [ ] Logs created in `logs/query_logs.jsonl`
- [ ] Stats endpoint returns data
- [ ] Frontend UI loads correctly

---

## 🎓 What You've Learned

1. **Multi-Source RAG**: Combining multiple data sources
2. **Fallback Logic**: Intelligent query routing
3. **LangChain Integration**: Production RAG patterns
4. **Metadata Enrichment**: Adding context to responses
5. **Vector Store Management**: FAISS operations
6. **API Design**: RESTful endpoints for ML systems
7. **UI/UX**: Information-rich chat interfaces

---

## 📚 Next Steps

1. **Add More Data**:
   - Expand `support_faqs.csv` to 100+ entries
   - Add more tickets to `support_tickets.csv`

2. **Improve Retrieval**:
   - Implement hybrid search (semantic + keyword)
   - Add reranking with cross-encoders

3. **Enhance UI**:
   - Add charts showing query distribution
   - Implement feedback buttons (👍👎)
   - Show trending questions

4. **Deploy**:
   - Package as Docker containers
   - Deploy to cloud (Render, Railway, GCP)
   - Add authentication

5. **Monitor**:
   - Set up Prometheus metrics
   - Add Grafana dashboards
   - Implement alerting

---

## 🤝 Support

**Having issues?** Check:
1. Logs in terminal
2. `logs/query_logs.jsonl` for errors
3. API health: `http://localhost:8000/health`
4. Vector stores exist: `data/vector_stores/`

**Still stuck?** Let me know and I'll help debug!

---

*Built with ❤️ using LangChain, FAISS, Gemini 2.0, and Streamlit*
