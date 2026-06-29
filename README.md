# SupportRAG — Dual Vector Store RAG Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Production-ready **Retrieval-Augmented Generation (RAG)** system with dual FAISS vector stores, an async job-queue platform, and a modern Next.js chat UI. Achieves **4.2x throughput** with **337 ms average latency** across **15,580+ documents**.

---

## What''s Inside

| Layer | Description |
|---|---|
| **`src/`** | Core RAG engine — FAISS IVF vector stores, LangChain pipeline, Groq LLM |
| **`frontend/`** | Next.js 16 chat UI — sends queries through the System Platform |
| **`platform/api/`** | FastAPI job-queue API — JWT auth, PostgreSQL, Redis |
| **`platform/worker/`** | Async RAG worker — polls Redis queue, runs the RAG pipeline, writes results |
| **`data/`** | CSV datasets (10,580 FAQs + 5,000 support tickets) |
| **`scripts/`** | Helper scripts — setup, rebuild vector stores, start services |
| **`tests/`** | Test suite |

---

## Architecture

```
Browser / curl
      |
      v
+------------------+   JWT   +----------------------------+
|  Next.js UI      | ------> |  System Platform API       |
|  localhost:3000  |         |  (FastAPI, port 8000)      |
+------------------+         +-------------+--------------+
                                           | lpush job_queue
                                           v
                                  +----------------+
                                  |    Redis        |
                                  |  (job queue)    |
                                  +-------+--------+
                                          | brpop
                                          v
                                  +----------------+
                                  |  RAG Worker     |
                                  |  (async worker) |
                                  +-------+--------+
                                          | imports directly
                                          v
                   +--------------------------------------------+
                   |    DualStoreRAGPipeline (src/)              |
                   |                                            |
                   |  +---------------+  +------------------+  |
                   |  |   FAQ Store   |  |   Ticket Store   |  |
                   |  |  10,580 docs  |  |    5,000 docs    |  |
                   |  |   FAISS IVF   |  |    FAISS IVF     |  |
                   |  +-------+-------+  +--------+---------+  |
                   |          +---------------+                 |
                   |                          v                 |
                   |          Fallback logic (65% threshold)    |
                   |                          v                 |
                   |              Groq Llama-3.3-70b            |
                   +--------------------+---------------------+
                                        |
                                        v
                              Answer + citations +
                              confidence + latency
```

**Key design:** The worker does **not** call the RAG engine over HTTP. It directly imports `DualStoreRAGPipeline` from `src/` and runs it in-process. This avoids an extra network hop.

---

## Performance

| Metric | Value |
|---|---|
| Documents | 15,580 (10,580 FAQs + 5,000 tickets) |
| Index type | FAISS IVF (205 / 141 clusters) |
| Avg latency (parallel) | **337 ms** |
| Throughput improvement | **4.2x** vs sequential |
| LLM | Groq Llama-3.3-70b-versatile |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop (for Postgres + Redis)
- [Groq API key](https://console.groq.com)

---

## Setup

### 1. Clone and create virtual environment

```powershell
git clone https://github.com/Sakshamyadav15/SupportRAG.git
cd SupportRAG

python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate          # macOS / Linux
```

### 2. Install Python dependencies

```powershell
pip install -r requirements.txt
pip install -r platform/api/requirements.txt
pip install -r platform/worker/requirements.txt
```

### 3. Configure environment

```powershell
copy .env.example .env
# Edit .env — set GROQ_API_KEY=your_key_here
```

### 4. Start infrastructure (Postgres + Redis)

```powershell
docker compose up -d postgres redis
```

> Postgres runs on **port 5433** and Redis on **port 6380** to avoid conflicts with local installations.

### 5. Build vector stores (one-time, ~3 minutes)

```python
python -c "from src.core.dual_rag_pipeline import DualStoreRAGPipeline; p = DualStoreRAGPipeline(); p.build_vector_stores(use_ivf=True); p.save_vector_stores(); print(''Done!'')"
```

---

## Running Locally

Open **three terminals**, all with the venv activated:

**Terminal 1 — System Platform API**
```powershell
cd platform/api
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — RAG Worker**
```powershell
cd platform/worker
python -m app.main
# Wait ~20s for "Worker running. Waiting for jobs..."
```

**Terminal 3 — Next.js Frontend**
```powershell
cd frontend
npm install        # first time only
npm run dev
# Open http://localhost:3000
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | Groq LLM API key |
| `DATABASE_URL` | No | `postgresql://postgres:password@127.0.0.1:5433/jobs` | Postgres connection |
| `REDIS_URL` | No | `redis://127.0.0.1:6380/0` | Redis connection |
| `SECRET_KEY` | No | dev default | JWT signing secret — **change in production** |
| `FAQ_SIMILARITY_THRESHOLD` | No | `0.65` | Confidence threshold before falling back to ticket store |

---

## Project Structure

```
SupportRAG/
├── src/                          # Core RAG engine
│   ├── core/dual_rag_pipeline.py # Main RAG logic — FAISS + Groq
│   ├── config/settings.py
│   ├── models/schemas.py
│   └── utils/
│
├── frontend/                     # Next.js 16 chat UI
│   ├── app/chat/page.tsx         # Chat interface
│   └── lib/api.ts                # API client (auth + job polling)
│
├── platform/                     # System Platform — async job queue
│   ├── api/                      # FastAPI job-queue API
│   │   └── app/
│   │       ├── api/routes/       # /auth, /jobs
│   │       ├── core/             # Config, DB, Redis
│   │       ├── models/           # SQLAlchemy models
│   │       └── services/         # Auth + job logic
│   └── worker/                   # Async RAG job worker
│       └── app/
│           ├── jobs/
│           │   └── support_rag_processor.py  # Bridges worker <-> RAG engine
│           └── worker.py         # Main poll loop
│
├── data/
│   ├── support_faqs.csv
│   ├── support_tickets.csv
│   └── vector_stores/            # FAISS indexes (gitignored)
│
├── scripts/                      # setup.ps1, rebuild_stores.py, etc.
├── tests/
├── docker-compose.yml            # Full-stack Docker deployment
├── nginx.conf                    # Gateway / load balancer config
├── Dockerfile                    # Standalone RAG API image
├── requirements.txt
└── .env.example
```

---

## API Reference

Interactive docs at `http://localhost:8000/docs`.

### Submit a job

```bash
# 1. Get a token
curl -X POST http://localhost:8000/auth/login \
  -d ''{"email":"you@example.com","password":"pass"}''

# 2. Submit a job
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d ''{"input_data": {"question": "How do I reset my password?", "top_k": 3}}''

# 3. Poll for result
curl http://localhost:8000/jobs/<id> -H "Authorization: Bearer <token>"
```

**Result payload** (when `status == "COMPLETED"`):
```json
{
  "answer": "To reset your password...",
  "source": "FAQ",
  "confidence": 0.87,
  "latency_ms": 342,
  "citations": [...]
}
```

---

## Docker Deployment (Full Stack)

```bash
docker compose up --build
# Access at http://localhost (Nginx proxy)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| RAG Framework | LangChain |
| Vector DB | FAISS (IVF clustered) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Groq Llama-3.3-70b-versatile |
| Platform API | FastAPI + SQLAlchemy + Pydantic |
| Job Queue | Redis |
| Database | PostgreSQL |
| Frontend | Next.js 16, Tailwind CSS, Radix UI |
| Gateway | Nginx |
| Auth | JWT (python-jose + passlib) |

---

## Roadmap

- [x] Dual FAISS IVF vector stores (FAQ + Ticket)
- [x] Async job queue platform (Redis + PostgreSQL)
- [x] Next.js chat UI with real-time job polling
- [x] JWT authentication
- [ ] Evaluation metrics (precision@k, recall@k, MRR)
- [ ] User feedback loop
- [ ] Hybrid search (BM25 + semantic)
- [ ] Multi-language support
- [ ] Query analytics dashboard

---

## Author

**Saksham Yadav** — [@Sakshamyadav15](https://github.com/Sakshamyadav15)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgments

- [LangChain](https://langchain.com) — RAG framework
- [HuggingFace](https://huggingface.co) — Bitext customer support dataset
- [Groq](https://groq.com) — Ultra-fast LLM inference
- [FAISS](https://github.com/facebookresearch/faiss) — Efficient vector similarity search
- [FastAPI](https://fastapi.tiangolo.com) — Async web framework
