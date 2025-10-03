# 🚀 SupportRAG Quick Reference

## Essential Commands

### Setup
```powershell
# Automated setup (Windows)
.\setup.ps1

# Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\init_vectordb.py
```

### Running the Application
```powershell
# Terminal 1: API Server
venv\Scripts\activate
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Frontend
venv\Scripts\activate
streamlit run frontend\app.py
```

### Access Points
- **Frontend UI**: http://localhost:8501
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Key Files to Know

### Configuration
- `.env` - Environment variables (API keys here!)
- `src/config/settings.py` - Application settings

### Core Logic
- `src/core/rag_pipeline.py` - Main RAG orchestration
- `src/core/embeddings.py` - Text to vectors
- `src/core/vectordb.py` - FAISS vector storage
- `src/core/llm.py` - LLM integration

### API
- `src/api/main.py` - FastAPI endpoints

### Frontend
- `frontend/app.py` - Streamlit UI

### Data
- `data/faqs.csv` - FAQ database
- `data/test_queries.csv` - Test queries

## Common Tasks

### Add New FAQs

**Method 1: Edit CSV**
```powershell
# 1. Edit data/faqs.csv
notepad data\faqs.csv

# 2. Reinitialize database
python scripts\init_vectordb.py
```

**Method 2: Via API**
```python
import requests
requests.post(
    "http://localhost:8000/api/v1/faq",
    json={
        "question": "Your question?",
        "answer": "Your answer.",
        "category": "general"
    }
)
```

**Method 3: Via Streamlit**
- Use sidebar → "Add New FAQ" expander

### Test Accuracy
```powershell
python scripts\evaluate.py
```

### Run Tests
```powershell
# All tests
pytest

# Specific test
pytest tests\test_embeddings.py

# With coverage
pytest --cov=src tests\
```

### View Logs
```powershell
# Application logs
type logs\app.log

# Metrics
type logs\metrics.json
```

### Reset Database
```powershell
# Delete vector store
Remove-Item -Recurse -Force data\vector_store

# Reinitialize
python scripts\init_vectordb.py
```

## API Endpoints Quick Reference

### Query
```bash
POST /api/v1/query
Body: {"question": "...", "top_k": 3}
```

### Add FAQ
```bash
POST /api/v1/faq
Body: {"question": "...", "answer": "...", "category": "..."}
```

### Get Metrics
```bash
GET /api/v1/metrics
```

### Health Check
```bash
GET /health
```

## Environment Variables

### Required
- `GEMINI_API_KEY` or `OPENAI_API_KEY`

### Optional (with defaults)
- `EMBEDDING_MODEL` (default: all-MiniLM-L6-v2)
- `LLM_PROVIDER` (default: gemini)
- `CONFIDENCE_THRESHOLD` (default: 0.7)
- `TOP_K_RESULTS` (default: 3)

## Configuration Tweaks

### Adjust Confidence Threshold
```python
# In .env
CONFIDENCE_THRESHOLD=0.8  # Higher = fewer escalations
```

### Change Embedding Model
```python
# In .env
EMBEDDING_MODEL=paraphrase-MiniLM-L6-v2
```

### Switch LLM Provider
```python
# In .env
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

## Troubleshooting Quick Fixes

### "Module not found"
```powershell
pip install -r requirements.txt
```

### "API key not found"
```powershell
# Check .env file has your key
notepad .env
```

### "Port already in use"
```powershell
# Use different port
uvicorn src.api.main:app --port 8001
```

### "Vector database empty"
```powershell
python scripts\init_vectordb.py
```

### "API shows offline in frontend"
```powershell
# Restart API server
uvicorn src.api.main:app --reload
```

## Docker Commands

### Build and Run
```powershell
docker-compose up -d
```

### View Logs
```powershell
docker-compose logs -f
```

### Stop Services
```powershell
docker-compose down
```

### Rebuild
```powershell
docker-compose up -d --build
```

## Development Workflow

### 1. Make Changes
Edit files in `src/`

### 2. Test Changes
```powershell
pytest tests\
```

### 3. Format Code
```powershell
black src\ tests\
```

### 4. Check Linting
```powershell
flake8 src\ tests\
```

### 5. Run Application
API auto-reloads with `--reload` flag

## Performance Tips

### Speed Up Queries
- Reduce `TOP_K_RESULTS` (fewer FAQs to process)
- Use smaller embedding model
- Enable caching (future feature)

### Improve Accuracy
- Add more diverse FAQs
- Increase `TOP_K_RESULTS`
- Fine-tune confidence threshold
- Improve FAQ quality and coverage

## File Size Reference

- **Small**: Config files, init files (< 1KB)
- **Medium**: Core modules (2-5KB)
- **Large**: API, pipeline (5-10KB)
- **Data**: FAQs CSV (10-50KB)
- **Generated**: Vector index (varies by FAQ count)

## Useful Python Snippets

### Direct Query (No API)
```python
from src.core.rag_pipeline import get_rag_pipeline
from src.models.schemas import QueryRequest

rag = get_rag_pipeline()
request = QueryRequest(question="How do I reset my password?")
response = rag.query(request)
print(response.answer)
```

### Add FAQ Programmatically
```python
from src.core.rag_pipeline import get_rag_pipeline
from src.models.schemas import FAQItem

rag = get_rag_pipeline()
faq = FAQItem(
    question="Test?",
    answer="Test answer.",
    category="test"
)
faq_id = rag.add_faq(faq)
```

### Get Metrics
```python
from src.core.rag_pipeline import get_rag_pipeline

rag = get_rag_pipeline()
metrics = rag.get_metrics()
print(f"Total queries: {metrics['total_queries']}")
```

## Important Notes

⚠️ **API Keys**: Never commit .env to git  
⚠️ **Vector DB**: Save after adding FAQs  
⚠️ **Dependencies**: Keep requirements.txt updated  
⚠️ **Tests**: Run before committing changes  
⚠️ **Logs**: Check logs/ for errors  

## Getting Help

1. **Check Logs**: `logs/app.log`
2. **Read Docs**: `docs/QUICKSTART.md`
3. **Run Tests**: `pytest -v`
4. **Check Health**: http://localhost:8000/health
5. **Review Examples**: `examples/usage_examples.py`

## Next Steps After Setup

1. ✅ Verify all tests pass
2. ✅ Run evaluation script
3. ✅ Add custom FAQs
4. ✅ Test with your queries
5. ✅ Deploy to cloud (optional)
6. ✅ Add to resume/portfolio

---

**Keep this file handy for quick reference! 📌**
