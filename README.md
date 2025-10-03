# SupportRAG - Retrieval-Augmented Generation for Customer Support

A production-ready RAG (Retrieval-Augmented Generation) application that provides intelligent answers to customer support FAQs using vector similarity search and LLM-powered response generation.

## 🎯 Features

- **Semantic Search**: Leverages sentence transformers for contextual FAQ retrieval
- **LLM Integration**: Uses Gemini API (or OpenAI GPT) for natural language responses
- **Citation Support**: Returns source FAQ references with each answer
- **Smart Escalation**: Automatically escalates low-confidence queries to human agents
- **Performance Monitoring**: Logs query latency, retrieval scores, and accuracy metrics
- **RESTful API**: FastAPI-powered backend with auto-generated documentation
- **Interactive UI**: Streamlit-based chat interface for easy interaction
- **Vector Database**: FAISS for efficient similarity search
- **Docker Ready**: Containerized deployment with nginx

## 🏗️ Architecture

```
User Query → Embedding → FAISS Retrieval → Context + Query → LLM → Response + Citations
                                ↓
                        (Low Confidence)
                                ↓
                        Human Escalation
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
