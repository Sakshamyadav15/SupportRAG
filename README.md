# 🤖 SupportRAG - AI-Powered Customer Support Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-ready **Retrieval-Augmented Generation (RAG)** system that transforms customer support by intelligently answering FAQs using vector search and Google Gemini 2.0 Flash LLM.

**🎯 Built for**: Google, Microsoft, Oracle, Swiggy, PhonePe internship applications

---

## 📸 Demo

> 🎥 **[Watch Demo Video](#)** | 🚀 **[Try Live Demo](#)** | 📖 **[Read Blog Post](#)**

<!-- Add screenshots here -->
```
[Screenshot 1: Chat Interface]
[Screenshot 2: High Confidence Answer with Citations]
[Screenshot 3: Metrics Dashboard]
```

---

## ✨ Key Features

### 🔍 **Intelligent Search**
- **Semantic Understanding**: Uses sentence-transformers (all-MiniLM-L6-v2) for 384-dimensional embeddings
- **FAISS Vector DB**: Sub-100ms retrieval on 1000+ FAQs
- **Cosine Similarity**: Accurate relevance scoring

### 🤖 **Smart Generation**
- **Gemini 2.0 Flash**: State-of-the-art LLM for natural responses
- **Context-Aware**: Retrieves top-K relevant FAQs before generating
- **Citation Tracking**: Every answer links back to source FAQs

### 🎯 **Confidence-Based Escalation**
- **70% Threshold**: Auto-escalates uncertain queries to humans
- **Quality Assurance**: Prevents hallucinations and incorrect answers
- **Transparency**: Shows confidence scores to users

### 📊 **Production Monitoring**
- **Real-time Metrics**: Tracks latency, confidence, escalation rates
- **Comprehensive Logging**: Query history with full traceability
- **Performance Analytics**: Response time distribution, accuracy trends

### 🛠️ **Developer-Friendly**
- **REST API**: 5 FastAPI endpoints with auto-generated docs
- **Type Safety**: Full Pydantic validation
- **Docker Ready**: One-command deployment
- **Extensible**: Easy to add new LLM providers or vector DBs

---

## 🏗️ Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Streamlit UI       │◄──── Interactive Chat Interface
│  (Frontend)         │
└──────┬──────────────┘
       │ HTTP
       ▼
┌─────────────────────┐
│  FastAPI Server     │◄──── REST API (5 endpoints)
│  (Backend)          │
└──────┬──────────────┘
       │
       ├─────────────┬─────────────┬──────────────┐
       │             │             │              │
       ▼             ▼             ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Embedding │  │ Vector   │  │   LLM    │  │ Metrics  │
│ Service  │  │Database  │  │ Service  │  │ Tracker  │
│(sentence)│  │ (FAISS)  │  │(Gemini)  │  │ (Logger) │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### RAG Pipeline Flow

```
1. Query: "How do I reset my password?"
         ↓
2. Embed: [0.23, -0.15, 0.87, ...] (384 dims)
         ↓
3. Search FAISS: Top 3 similar FAQs
         ↓
4. Context: FAQ1 (score: 0.85) + FAQ2 (score: 0.72) + FAQ3 (score: 0.65)
         ↓
5. Generate: Gemini 2.0 with context
         ↓
6. Response: "To reset your password, go to the login page..."
         ↓
7. Citations: Shows source FAQs with confidence scores
```

## 📁 Project Structure

```
SupportRAG/
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core RAG logic
│   ├── models/                 # Data models
│   ├── utils/                  # Utilities
│   └── config/                 # Configuration
├── data/                       # FAQ data and vector stores
├── tests/                      # Test suite
├── frontend/                   # Streamlit UI
├── logs/                       # Application logs
├── scripts/                    # Utility scripts
├── docker/                     # Docker configuration
└── docs/                       # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip or conda
- Gemini API Key (or OpenAI API Key)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/SupportRAG.git
cd SupportRAG
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Initialize vector database**
```bash
python scripts/init_vectordb.py
```

6. **Run the application**
```bash
# Start FastAPI backend
uvicorn src.api.main:app --reload --port 8000

# In another terminal, start Streamlit frontend
streamlit run frontend/app.py
```

## 🔧 Configuration

Edit `src/config/settings.py` or use environment variables:

- `GEMINI_API_KEY`: Your Gemini API key
- `EMBEDDING_MODEL`: Default is `all-MiniLM-L6-v2`
- `VECTOR_DB_PATH`: Path to FAISS index
- `CONFIDENCE_THRESHOLD`: Minimum score for auto-response (default: 0.7)
- `TOP_K_RESULTS`: Number of FAQs to retrieve (default: 3)

## 📊 API Endpoints

### Health Check
```
GET /health
```

### Query Endpoint
```
POST /api/v1/query
{
  "question": "How do I reset my password?",
  "top_k": 3
}
```

### Add FAQ
```
POST /api/v1/faq
{
  "question": "How to reset password?",
  "answer": "Go to settings...",
  "category": "account"
}
```

### Metrics
```
GET /api/v1/metrics
```

## 🧪 Testing

Run the test suite:
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_retrieval.py

# With coverage
pytest --cov=src tests/
```

Run accuracy evaluation:
```bash
python scripts/evaluate.py
```

## 📈 Performance Metrics

The application tracks:
- **Query Latency**: End-to-end response time
- **Retrieval Score**: Cosine similarity scores
- **Hit Rate**: % of queries answered vs escalated
- **Response Quality**: Manual evaluation scores

Metrics are logged to `logs/metrics.json` and can be viewed via the `/metrics` endpoint.

## 🐳 Docker Deployment

```bash
# Build image
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the application at `http://localhost:80`

## 📝 Adding Custom FAQs

1. **Via API**: POST to `/api/v1/faq`
2. **Via CSV**: Add to `data/faqs.csv` and run `python scripts/init_vectordb.py`
3. **Programmatically**: Use the `FAQManager` class

## 🛠️ Development

### Code Style
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 📚 Tech Stack

- **Backend**: FastAPI 0.104+
- **RAG Framework**: LangChain 0.1+
- **Embeddings**: sentence-transformers
- **Vector DB**: FAISS
- **LLM**: Google Gemini API / OpenAI GPT
- **Frontend**: Streamlit
- **Deployment**: Docker, Nginx, Uvicorn

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced caching layer
- [ ] Fine-tuned retrieval model
- [ ] A/B testing framework
- [ ] Analytics dashboard
- [ ] User feedback loop
- [ ] Integration with Slack/Discord

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## 📧 Contact

Saksham - [Your Email/LinkedIn]

Project Link: https://github.com/yourusername/SupportRAG
