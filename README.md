# SupportRAG + System Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository contains **two tightly integrated systems**:

| System | What it does |
|---|---|
| **SupportRAG** | Dual FAISS vector store RAG engine — 15,580+ documents, FAISS IVF indexing, Groq Llama-3 |
| **System Platform** | Distributed job processing platform — Redis queues, PostgreSQL state, Nginx load balancing, horizontally scalable workers |

The two are **wired together**: the System Platform''s async workers process jobs by running the SupportRAG pipeline in-process (no extra HTTP hop), delivering RAG answers to a Next.js chat UI.

---

## SupportRAG — Dual Vector Store RAG Engine

### How it works

Queries are answered using a **dual-store retrieval strategy**:

1. Search the **FAQ Store** (10,580 documents, FAISS IVF, 205 clusters)
2. If top similarity score < 65% threshold → fall back to **Ticket Store** (5,000 historical tickets, FAISS IVF, 141 clusters)
3. Top-K documents are passed to **Groq Llama-3.3-70b** for grounded answer generation
4. Response includes answer, source (FAQ/TICKET), confidence score, citations, and latency

### Performance

| Metric | Value |
|---|---|
| Total documents | 15,580 (10,580 FAQs + 5,000 tickets) |
| Index type | FAISS IVF (clustered) |
| Avg query latency | **337 ms** (parallel mode) |
| Throughput improvement | **4.2x** vs sequential |
| LLM | Groq Llama-3.3-70b-versatile |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 |

### Architecture

```mermaid
graph TB
    USER["  User Query  "]

    subgraph PIPELINE["  DualStoreRAGPipeline  "]
        direction TB
        
        subgraph SEARCH["  Parallel Search (ThreadPoolExecutor)  "]
            FAQ["FAQ Store\n10,580 Docs\nFAISS IVF"]
            TICKET["Ticket Store\n5,000 Docs\nFAISS"]
        end
        
        FALLBACK{"Fallback Logic\nFAQ Conf < 65%?"}
        LLM["Groq Llama-3.3-70b"]
        
        FAQ --> FALLBACK
        TICKET -.-> FALLBACK
        FALLBACK --> LLM
    end

    USER --> PIPELINE
    PIPELINE --> OUTPUT["  Answer + Citations\nConfidence + Latency  "]

    style USER fill:#2196F3,color:#fff,stroke:none
    style OUTPUT fill:#4CAF50,color:#fff,stroke:none
    style FAQ fill:#FF9800,color:#fff,stroke:none
    style TICKET fill:#E91E63,color:#fff,stroke:none
    style FALLBACK fill:#9C27B0,color:#fff,stroke:none
    style LLM fill:#455A64,color:#fff,stroke:none

    style PIPELINE fill:#0a1a2a,stroke:#2196F3,stroke-width:1px,color:#aaa
    style SEARCH fill:#2a1800,stroke:#FF9800,stroke-width:1px,color:#aaa
```

---

## System Platform — Distributed Job Processing

### Overview

The System Platform is a production-grade distributed job processing system built independently of the RAG engine and designed for **horizontal scalability**. It manages the full lifecycle of RAG jobs: ingestion, queuing, dispatch, execution, persistence, and result retrieval.

```mermaid
graph TB
    BROWSER["  Browser  "]

    subgraph GATEWAY["  Gateway Layer  "]
        NGINX["Nginx Gateway\nReverse Proxy\nRate Limiting (30r/s)"]
    end

    subgraph APPLAYER["  API Replicas (FastAPI)  "]
        direction LR
        API1["API-1\n:8000"]
        API2["API-2\n:8000"]
    end

    subgraph QUEUE["  Message Broker  "]
        REDIS["Redis\njob_queue (LPUSH / BRPOP)\nRate limits + Cache"]
    end

    subgraph WORKERS["  Scalable Worker Nodes  "]
        direction LR
        W1["Worker-1"]
        W2["Worker-2"]
    end

    subgraph PIPELINES["  In-Process RAG  "]
        RAG1["DualStoreRAGPipeline"]
        RAG2["DualStoreRAGPipeline"]
    end

    subgraph DB["  Persistent Storage  "]
        PG["PostgreSQL\nPersistent job state"]
    end

    BROWSER --> GATEWAY
    GATEWAY --> APPLAYER
    API1 -- lpush job_id --> REDIS
    API2 -- lpush job_id --> REDIS
    REDIS -- brpop --> WORKERS
    
    W1 --> RAG1
    W2 --> RAG2

    RAG1 --> DB
    RAG2 --> DB

    style BROWSER fill:#2196F3,color:#fff,stroke:none
    style NGINX fill:#9C27B0,color:#fff,stroke:none
    style API1 fill:#4CAF50,color:#fff,stroke:none
    style API2 fill:#4CAF50,color:#fff,stroke:none
    style REDIS fill:#E91E63,color:#fff,stroke:none
    style W1 fill:#FF9800,color:#fff,stroke:none
    style W2 fill:#FF9800,color:#fff,stroke:none
    style RAG1 fill:#455A64,color:#fff,stroke:none
    style RAG2 fill:#455A64,color:#fff,stroke:none
    style PG fill:#1D9E75,color:#fff,stroke:none

    style GATEWAY fill:#1a0a2a,stroke:#9C27B0,stroke-width:1px,color:#aaa
    style APPLAYER fill:#0a2a0a,stroke:#4CAF50,stroke-width:1px,color:#aaa
    style QUEUE fill:#2a0a18,stroke:#E91E63,stroke-width:1px,color:#aaa
    style WORKERS fill:#2a1800,stroke:#FF9800,stroke-width:1px,color:#aaa
    style PIPELINES fill:#1a1a1a,stroke:#555,stroke-width:1px,color:#aaa
    style DB fill:#0a2a22,stroke:#1D9E75,stroke-width:1px,color:#aaa
```

### Key Engineering Decisions

#### 1. Redis-Backed Priority Queue

```python
# platform/api/app/queue/job_queue.py

class JobQueue:
    # LPUSH for FIFO with BRPOP — O(1) enqueue and dequeue
    def enqueue(self, job_id: int, priority: int = 0) -> bool:
        message = {"job_id": job_id, "enqueued_at": ..., "priority": priority}
        self.redis.lpush(self.queue_name, json.dumps(message))

    def dequeue(self, timeout: int = 0) -> Optional[dict]:
        result = self.redis.brpop([self.queue_name], timeout=timeout)
        # BRPOP blocks until a job arrives — zero CPU spin

    def requeue(self, job_id: int) -> bool:
        return self.enqueue(job_id, priority=-1)  # lower priority for retries
```

- **LPUSH + BRPOP** gives FIFO semantics with O(1) operations
- Workers use **blocking pop** — no polling loop, zero CPU usage while idle
- Priority field reserved for future priority queue extension
- Graceful degradation: if Redis is down, job is immediately marked FAILED in PostgreSQL

#### 2. Token-Bucket Rate Limiting (Two Layers)

**Layer 1 — Nginx network-level:**
```nginx
# nginx.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

location / {
    limit_req zone=api_limit burst=20 nodelay;
    limit_conn conn_limit 10;
    proxy_next_upstream error timeout http_502 http_503;  # Auto failover
}
```

**Layer 2 — Application-level (Redis-backed per user/IP):**
```python
# platform/api/app/middleware/rate_limiter.py

class TokenBucket:
    def consume(self, identifier: str) -> tuple[bool, dict]:
        # Atomic Redis pipeline: GET tokens, calculate refill, SET new value
        # Falls back gracefully if Redis is unavailable (allow all)
        ...
    # Identifier = user_id from JWT (authenticated) or IP (anonymous)
    # Response headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

**Layer 3 — Groq API rate limiting (per-worker sliding window):**
```python
# platform/worker/app/jobs/support_rag_processor.py

class GroqRateLimiter:
    # Sliding-window: 30 req/min, 6000 tokens/min
    async def acquire(self, estimated_tokens: int = 800):
        # Blocks in 100ms increments — no errors thrown, no retries needed
        while not capacity_available:
            await asyncio.sleep(0.1)
```

#### 3. Multi-Layer Caching

```python
# platform/api/app/services/cache_service.py

class CacheService:
    # Read-through: check Redis first, fall through to PostgreSQL on miss
    def get_job(self, job_id: int) -> Optional[dict]: ...

    # Write-through: update Redis on every DB write
    def set_job(self, job: Job) -> bool: ...

    # Invalidation: cache busted on every job state transition
    def invalidate_job(self, job_id: int) -> bool: ...
```

Cache key namespaces:
- `cache:job:{id}` — individual job (TTL: 300s)
- `cache:job_list:{user_id}:{skip}:{limit}` — paginated lists
- `rate_limit:{user/ip}:tokens` — rate limit buckets

#### 4. Persistent Job State + Fault Tolerance

```mermaid
graph LR
    PENDING["  PENDING  "]
    PROCESSING["  PROCESSING  "]
    COMPLETED["  COMPLETED  "]
    FAILED["  FAILED  "]

    PENDING -- worker picks up --> PROCESSING
    PROCESSING -- success --> COMPLETED
    PROCESSING -- exception --> FAILED
    FAILED -- requeue (retry) --> PENDING
    
    style PENDING fill:#FF9800,color:#fff,stroke:none
    style PROCESSING fill:#2196F3,color:#fff,stroke:none
    style COMPLETED fill:#4CAF50,color:#fff,stroke:none
    style FAILED fill:#D32F2F,color:#fff,stroke:none
```

- Every state transition is **written to PostgreSQL before** the worker acts — no lost jobs on crash
- Worker catches all exceptions and marks job FAILED (never silently drops)
- Jobs survive worker crashes: a new worker polls the same Redis queue and re-processes
- Cache is **invalidated** on every state transition so clients always see fresh data

```python
# platform/worker/app/worker.py — fault-tolerant worker loop
async def _process_job(self, job_id: int):
    job.status = JobStatus.PROCESSING
    db.commit()                        # Committed before any processing
    try:
        result = await processor.process(job_wrapper)
        job.status = JobStatus.COMPLETED
        db.commit()
    except Exception as exc:
        self._fail_job(db, job, str(exc))  # Always marks FAILED, never drops
    finally:
        self._invalidate_cache(job_id)     # Cache always invalidated
```

#### 5. Horizontal Scaling

- **API layer**: Any number of FastAPI replicas behind Nginx (`least_conn` load balancing, keep-alive pooling, auto failover on 502/503/504)
- **Worker layer**: Any number of worker processes independently polling the same Redis queue — add workers with `docker compose scale worker=N`
- **Stateless API**: No in-memory state; all coordination via Redis + PostgreSQL
- **No data loss on scale-out**: Redis queue is the single source of truth for pending jobs; PostgreSQL is the source of truth for job state

---

## Integrated Flow: End-to-End

```mermaid
sequenceDiagram
    participant USER as User
    participant UI as Next.js UI
    participant API as FastAPI
    participant DB as PostgreSQL
    participant REDIS as Redis
    participant WORKER as Background Worker

    USER->>UI: Types question
    UI->>API: POST /jobs (JWT Auth)
    API->>DB: Creates Job (status=PENDING)
    API->>REDIS: lpush job_id
    API-->>UI: returns {id, status="PENDING"}
    
    loop Every 1 second
        UI->>API: Polls GET /jobs/{id}
    end
    
    WORKER->>REDIS: BRPOP blocks on queue
    REDIS-->>WORKER: Receives job_id
    WORKER->>DB: Marks Job (status=PROCESSING)
    WORKER->>WORKER: Runs DualStoreRAGPipeline.aquery()
    WORKER->>DB: Marks Job (status=COMPLETED)
    WORKER->>REDIS: Invalidates job cache
    
    API-->>UI: Returns {status="COMPLETED", data=...}
    UI-->>USER: Displays answer & citations
```

---

## Project Structure

```
SupportRAG/
├── src/                            # RAG Engine
│   ├── core/dual_rag_pipeline.py   # DualStoreRAGPipeline — FAISS + Groq
│   ├── config/settings.py          # Pydantic settings
│   ├── models/schemas.py           # Pydantic response schemas
│   └── utils/                      # Logger, metrics
│
├── frontend/                       # Next.js 16 Chat UI
│   ├── app/chat/page.tsx           # Chat interface with polling
│   └── lib/api.ts                  # Auth + job submit + polling client
│
├── platform/                       # System Platform
│   ├── api/                        # FastAPI Job Queue API
│   │   └── app/
│   │       ├── api/routes/         # POST /jobs, GET /jobs/{id}, /auth
│   │       ├── middleware/
│   │       │   └── rate_limiter.py # Token-bucket (Redis-backed)
│   │       ├── queue/
│   │       │   └── job_queue.py    # LPUSH / BRPOP queue operations
│   │       ├── services/
│   │       │   ├── job_service.py  # Job lifecycle + cache orchestration
│   │       │   └── cache_service.py# Read-through + write-through cache
│   │       └── models/job.py       # SQLAlchemy: PENDING/PROCESSING/COMPLETED/FAILED
│   └── worker/                     # Async RAG Job Worker
│       └── app/
│           ├── jobs/
│           │   ├── processor.py              # Registry pattern (extensible)
│           │   └── support_rag_processor.py  # Groq rate limiter + pipeline bridge
│           └── worker.py                     # Fault-tolerant BRPOP poll loop
│
├── data/                           # Datasets
│   ├── support_faqs.csv            # 580 local FAQs
│   ├── support_tickets.csv         # 5,000 support tickets
│   └── vector_stores/              # FAISS indexes (gitignored — build locally)
│
├── scripts/                        # Setup, rebuild, start scripts
├── tests/
├── docker-compose.yml              # Full stack: API x2, Worker x2, Redis, Postgres, Nginx
├── nginx.conf                      # Load balancer config
└── Dockerfile                      # Standalone RAG API image
```

---

## Setup & Running

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop
- [Groq API key](https://console.groq.com) (free tier)

### 1. Clone and set up environment

```powershell
git clone https://github.com/Sakshamyadav15/SupportRAG.git
cd SupportRAG

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r platform/api/requirements.txt
pip install -r platform/worker/requirements.txt

copy .env.example .env
# Set GROQ_API_KEY=your_key_here in .env
```

### 2. Start infrastructure

```powershell
docker compose up -d postgres redis
# Postgres: localhost:5433   Redis: localhost:6380
```

### 3. Build vector stores (once, ~3 minutes)

```python
python -c "
from src.core.dual_rag_pipeline import DualStoreRAGPipeline
p = DualStoreRAGPipeline()
p.build_vector_stores(use_ivf=True)
p.save_vector_stores()
"
```

### 4. Run all three services

**Terminal 1 — API**
```powershell
cd platform/api
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Worker**
```powershell
cd platform/worker
python -m app.main
# Wait for: "Worker running. Waiting for jobs..."
```

**Terminal 3 — Frontend**
```powershell
cd frontend
npm install && npm run dev
# Open http://localhost:3000
```

### Full Docker Deployment

```bash
docker compose up --build
# http://localhost  (Nginx, load-balanced)
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | **Required.** Groq LLM API key |
| `DATABASE_URL` | `postgresql://postgres:password@127.0.0.1:5433/jobs` | PostgreSQL |
| `REDIS_URL` | `redis://127.0.0.1:6380/0` | Redis |
| `SECRET_KEY` | dev default | JWT signing key — **change in production** |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60` | API rate limit per user/IP |
| `RATE_LIMIT_BURST_SIZE` | `10` | Token bucket burst capacity |
| `CACHE_ENABLED` | `true` | Enable Redis job cache |
| `CACHE_TTL_SECONDS` | `300` | Cache TTL |
| `FAQ_SIMILARITY_THRESHOLD` | `0.65` | Fallback to Ticket Store below this confidence |
| `GROQ_REQUESTS_PER_MINUTE` | `30` | Groq rate limit (free tier) |
| `GROQ_TOKENS_PER_MINUTE` | `6000` | Groq token budget per minute |

---

## API Reference

Interactive docs: `http://localhost:8000/docs`

### Auth

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d ''{"email":"user@example.com","password":"yourpassword"}''

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d ''{"email":"user@example.com","password":"yourpassword"}''
# Returns: {"access_token": "...", "token_type": "bearer"}
```

### Jobs

```bash
# Submit a RAG job
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d ''{"input_data": {"question": "How do I reset my password?", "top_k": 3}}''
# Returns: {"id": 42, "status": "PENDING", ...}

# Poll for result
curl http://localhost:8000/jobs/42 \
  -H "Authorization: Bearer <token>"
# Returns when COMPLETED:
# {"status": "COMPLETED", "result_data": "{\"answer\":\"...\",\"source\":\"FAQ\",\"confidence\":0.87,...}"}
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
| Job Queue | Redis (LPUSH/BRPOP) |
| Database | PostgreSQL 15 |
| Caching | Redis (read-through + write-through) |
| Rate Limiting | Token bucket (Redis-backed, 2-layer with Nginx) |
| Gateway | Nginx (least_conn load balancing + failover) |
| Frontend | Next.js 16, Tailwind CSS, Radix UI |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Containers | Docker Compose |

---

## Roadmap

- [x] Dual FAISS IVF vector stores
- [x] Async job queue platform (Redis + PostgreSQL)
- [x] Token-bucket rate limiting (Nginx + Redis + Groq)
- [x] Multi-layer caching (Redis read-through + write-through)
- [x] Horizontally scalable workers + Nginx load balancing
- [x] Fault-tolerant job state machine (PENDING/PROCESSING/COMPLETED/FAILED)
- [x] Next.js chat UI
- [x] JWT authentication
- [ ] Priority queue (field reserved, backend not yet wired)
- [ ] Evaluation metrics (precision@k, recall@k, MRR)
- [ ] Hybrid search (BM25 + semantic)
- [ ] User feedback loop
- [ ] Multi-language support

---

## Author

**Saksham Yadav** — [@Sakshamyadav15](https://github.com/Sakshamyadav15)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgments

- [LangChain](https://langchain.com) — RAG orchestration
- [HuggingFace](https://huggingface.co) — Bitext customer support dataset (26.8k records)
- [Groq](https://groq.com) — Ultra-fast LLM inference
- [FAISS](https://github.com/facebookresearch/faiss) — Efficient vector similarity search
- [FastAPI](https://fastapi.tiangolo.com) — Async web framework
