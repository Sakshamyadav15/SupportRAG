# Quick Start Guide

This guide will help you get SupportRAG up and running in under 10 minutes.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git
- API key for Gemini or OpenAI

## Step 1: Clone and Setup

```powershell
# Clone the repository
git clone https://github.com/yourusername/SupportRAG.git
cd SupportRAG

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your favorite editor
notepad .env
```

**Required Configuration:**
```env
GEMINI_API_KEY=your_actual_api_key_here
# OR
OPENAI_API_KEY=your_actual_api_key_here
```

**Get API Keys:**
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

## Step 3: Initialize Vector Database

```powershell
# Load FAQs and create vector index
python scripts/init_vectordb.py
```

**Expected Output:**
```
Loading FAQs from data/faqs.csv
Loaded 20 FAQs from CSV
Adding FAQs to vector database...
Successfully added 20 FAQs
Vector database saved to data/vector_store
```

## Step 4: Start the API Server

```powershell
# Terminal 1: Start FastAPI backend
uvicorn src.api.main:app --reload --port 8000
```

**Verify API is running:**
- Open browser: http://localhost:8000
- Check health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Step 5: Start the Frontend

```powershell
# Terminal 2: Start Streamlit frontend
streamlit run frontend/app.py
```

**Access the app:**
- Browser will open automatically at http://localhost:8501
- Or manually open: http://localhost:8501

## Step 6: Test the System

### Try These Example Queries:

1. **Account Management**
   - "How do I reset my password?"
   - "Can I update my billing information?"

2. **Orders & Shipping**
   - "Where is my order?"
   - "How long does shipping take?"

3. **Returns & Refunds**
   - "What is your return policy?"
   - "My item arrived damaged"

## Verification Checklist

✅ Python 3.9+ installed  
✅ Dependencies installed  
✅ API key configured  
✅ Vector database initialized  
✅ API server running (port 8000)  
✅ Frontend running (port 8501)  
✅ Test query successful  

## Troubleshooting

### API Won't Start

**Error:** `ModuleNotFoundError`
```powershell
pip install -r requirements.txt
```

**Error:** `API key not found`
- Check `.env` file exists
- Verify API key is correct
- Restart the server

### Frontend Shows "API Offline"

- Ensure API is running on port 8000
- Check API health: http://localhost:8000/health
- Verify no firewall blocking

### "No FAQs found" Error

```powershell
# Reinitialize database
python scripts/init_vectordb.py
```

### Import Errors

```powershell
# Ensure you're in the project root
cd SupportRAG

# Activate virtual environment
venv\Scripts\activate
```

## Next Steps

### Run Tests
```powershell
pytest tests/
```

### Evaluate Performance
```powershell
python scripts/evaluate.py
```

### Add Custom FAQs

**Option 1: Via API**
```python
import requests

requests.post(
    "http://localhost:8000/api/v1/faq",
    json={
        "question": "Your question?",
        "answer": "Your answer.",
        "category": "custom"
    }
)
```

**Option 2: Via CSV**
1. Edit `data/faqs.csv`
2. Run `python scripts/init_vectordb.py`

### View Metrics
- Open http://localhost:8000/api/v1/metrics
- Or use the Streamlit sidebar

## Docker Deployment (Optional)

```powershell
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost
```

## Development Mode

```powershell
# Enable hot reload
uvicorn src.api.main:app --reload

# Run tests on file changes
pytest-watch
```

## Production Deployment

See `docs/DEPLOYMENT.md` for production setup including:
- Environment configuration
- Database optimization
- Security hardening
- Monitoring setup
- Scaling strategies

## Getting Help

- **Documentation**: Check `docs/` folder
- **API Reference**: http://localhost:8000/docs
- **Issues**: Open a GitHub issue
- **Examples**: See `examples/` folder

## What's Next?

Now that you have SupportRAG running:

1. **Customize**: Add your own FAQs
2. **Evaluate**: Test accuracy with your queries
3. **Integrate**: Connect to your systems
4. **Deploy**: Move to production
5. **Monitor**: Track performance metrics

Happy building! 🚀
