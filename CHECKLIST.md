# ✅ SupportRAG Setup Checklist

Use this checklist to ensure everything is set up correctly.

## Pre-Setup Checklist

- [ ] Python 3.9 or higher installed
  ```powershell
  python --version
  ```

- [ ] pip is working
  ```powershell
  pip --version
  ```

- [ ] Git installed (for version control)
  ```powershell
  git --version
  ```

- [ ] Code editor ready (VS Code recommended)

- [ ] Have a Gemini API key OR OpenAI API key
  - Gemini: https://makersuite.google.com/app/apikey
  - OpenAI: https://platform.openai.com/api-keys

## Installation Checklist

- [ ] Virtual environment created
  ```powershell
  python -m venv venv
  ```

- [ ] Virtual environment activated
  ```powershell
  venv\Scripts\activate
  ```

- [ ] Dependencies installed
  ```powershell
  pip install -r requirements.txt
  ```

- [ ] .env file created from template
  ```powershell
  copy .env.example .env
  ```

- [ ] API key added to .env file
  ```env
  GEMINI_API_KEY=your_actual_key_here
  ```

- [ ] Directories created
  ```powershell
  mkdir logs
  mkdir data\vector_store
  ```

## Database Initialization Checklist

- [ ] FAQs CSV file exists at `data/faqs.csv`

- [ ] Vector database initialized
  ```powershell
  python scripts\init_vectordb.py
  ```

- [ ] Initialization successful (check output for "Initialization Complete")

- [ ] Vector store files created:
  - [ ] `data/vector_store/faq_index.index`
  - [ ] `data/vector_store/faqs.pkl`
  - [ ] `data/vector_store/metadata.json`

## Testing Checklist

- [ ] Unit tests run successfully
  ```powershell
  pytest tests\test_embeddings.py
  pytest tests\test_vectordb.py
  ```

- [ ] All tests pass (0 failures)

- [ ] Example usage works
  ```powershell
  python examples\usage_examples.py
  ```

## API Server Checklist

- [ ] API server starts without errors
  ```powershell
  uvicorn src.api.main:app --reload
  ```

- [ ] API accessible at http://localhost:8000

- [ ] Health check returns OK
  - Visit: http://localhost:8000/health
  - Should see: `{"status": "healthy", ...}`

- [ ] API documentation loads
  - Visit: http://localhost:8000/docs
  - Swagger UI should be visible

- [ ] Can execute test query from /docs
  ```json
  {
    "question": "How do I reset my password?",
    "top_k": 3
  }
  ```

## Frontend Checklist

- [ ] Streamlit starts without errors
  ```powershell
  streamlit run frontend\app.py
  ```

- [ ] Frontend accessible at http://localhost:8501

- [ ] API status shows "✅ API Connected" in sidebar

- [ ] Can type a message in chat input

- [ ] Receives response with answer

- [ ] Citations appear in expandable section

- [ ] Metrics display in sidebar

## Feature Testing Checklist

### Basic Functionality
- [ ] Ask a question about passwords → Get relevant answer
- [ ] Ask about business hours → Get relevant answer
- [ ] Ask about orders → Get relevant answer

### Citations
- [ ] Answers include citation sources
- [ ] Similarity scores are displayed
- [ ] Can expand to see full FAQ text

### Escalation
- [ ] Ask unrelated question → Should escalate
  - Try: "What is the meaning of life?"
- [ ] Escalation message appears
- [ ] Escalated flag is true

### FAQ Management
- [ ] Can add new FAQ via Streamlit sidebar
- [ ] New FAQ appears in search results
- [ ] Can add FAQ via API endpoint

### Metrics
- [ ] Metrics update after queries
- [ ] Total queries increases
- [ ] Average latency is reasonable (<500ms)
- [ ] Confidence scores make sense (0-1 range)

## Performance Checklist

- [ ] Query response time < 500ms average

- [ ] Embedding generation works

- [ ] Vector search returns results

- [ ] LLM generates coherent answers

- [ ] No memory leaks during multiple queries

## Evaluation Checklist

- [ ] Test queries CSV exists at `data/test_queries.csv`

- [ ] Evaluation script runs
  ```powershell
  python scripts\evaluate.py
  ```

- [ ] Evaluation completes successfully

- [ ] Results saved to `logs/evaluation_results.csv`

- [ ] Accuracy metrics are reasonable:
  - [ ] Accuracy@1 > 70%
  - [ ] Accuracy@3 > 85%

## Docker Deployment Checklist (Optional)

- [ ] Docker Desktop installed and running

- [ ] docker-compose.yml exists

- [ ] Build succeeds
  ```powershell
  docker-compose build
  ```

- [ ] Containers start
  ```powershell
  docker-compose up -d
  ```

- [ ] Services are running
  ```powershell
  docker-compose ps
  ```

- [ ] Can access via nginx at http://localhost

## Documentation Checklist

- [ ] README.md is clear and complete

- [ ] QUICKSTART.md guides you through setup

- [ ] API.md documents all endpoints

- [ ] ARCHITECTURE.md explains the system

- [ ] PROJECT_SUMMARY.md is ready for resume

## Git Repository Checklist (Recommended)

- [ ] Git repository initialized
  ```powershell
  git init
  ```

- [ ] .gitignore is in place

- [ ] Initial commit made
  ```powershell
  git add .
  git commit -m "Initial commit: Complete SupportRAG implementation"
  ```

- [ ] Pushed to GitHub
  ```powershell
  git remote add origin https://github.com/yourusername/SupportRAG.git
  git push -u origin main
  ```

- [ ] Repository has good README

- [ ] Repository is public (for resume)

## Resume/Portfolio Checklist

- [ ] Add project to GitHub profile

- [ ] Add to resume under "Projects" section

- [ ] Add to LinkedIn featured projects

- [ ] Prepare demo for interviews:
  - [ ] Can start and show in <2 minutes
  - [ ] Can explain architecture
  - [ ] Know the tech stack well
  - [ ] Can discuss trade-offs

- [ ] Optional: Create demo video
  - [ ] Screen recording of using the system
  - [ ] Upload to YouTube/LinkedIn
  - [ ] Add link to resume

## Interview Preparation Checklist

### Technical Questions Ready
- [ ] Explain RAG architecture
- [ ] Why FAISS over other vector DBs?
- [ ] Why sentence-transformers?
- [ ] How does escalation work?
- [ ] How would you scale this?

### Code Walkthrough Ready
- [ ] Can explain embeddings.py
- [ ] Can explain vectordb.py
- [ ] Can explain rag_pipeline.py
- [ ] Can explain API design choices

### Metrics Ready
- [ ] Know your accuracy numbers
- [ ] Know average latency
- [ ] Know escalation rate
- [ ] Know how many test cases

## Troubleshooting Checklist

If something doesn't work:

- [ ] Virtual environment activated?
- [ ] All dependencies installed?
- [ ] .env file has API key?
- [ ] Vector database initialized?
- [ ] API server running on port 8000?
- [ ] No firewall blocking ports?
- [ ] Check logs in `logs/app.log`
- [ ] Try restarting services

## Final Verification

Run through this complete workflow:

1. [ ] Start fresh terminal
2. [ ] Activate venv: `venv\Scripts\activate`
3. [ ] Start API: `uvicorn src.api.main:app --reload`
4. [ ] New terminal, activate venv
5. [ ] Start frontend: `streamlit run frontend\app.py`
6. [ ] Open http://localhost:8501
7. [ ] Ask: "How do I reset my password?"
8. [ ] Receive answer with citations
9. [ ] Check metrics in sidebar
10. [ ] Everything works! ✅

## Success Criteria

Your setup is complete when:

✅ API returns answers in <500ms  
✅ Answers include relevant citations  
✅ Low-confidence queries escalate  
✅ Metrics track correctly  
✅ Tests all pass  
✅ Evaluation shows >70% accuracy  
✅ Documentation is clear  
✅ Can demo in interviews  

---

**Congratulations! You now have a production-ready RAG system! 🎉**

Next: Start customizing with your own FAQs and deploy to the cloud!
