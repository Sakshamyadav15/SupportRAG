# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                  (Streamlit / Web Client)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              RAG Pipeline Orchestrator                │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │  Embedding  │  │  Vector DB   │  │    LLM     │  │  │
│  │  │   Service   │─▶│   (FAISS)    │─▶│  Service   │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│         ┌──────────────────┬──────────────────┐            │
│         │  Gemini API      │  OpenAI API      │            │
│         └──────────────────┴──────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Embedding Service (`src/core/embeddings.py`)

**Purpose**: Convert text to dense vector representations

**Technology**: sentence-transformers (all-MiniLM-L6-v2)

**Key Features**:
- Single and batch text embedding
- Cosine similarity calculation
- 384-dimensional vectors
- Cached model loading

**Flow**:
```
Text Input → Tokenization → Model Encoding → Vector Output
```

### 2. Vector Database (`src/core/vectordb.py`)

**Purpose**: Store and retrieve FAQ embeddings

**Technology**: FAISS (Facebook AI Similarity Search)

**Key Features**:
- IndexFlatIP for cosine similarity
- Batch insertion
- Top-K similarity search
- Persistence to disk

**Storage**:
- Index: `data/vector_store/faq_index.index`
- FAQs: `data/vector_store/faqs.pkl`
- Metadata: `data/vector_store/metadata.json`

### 3. LLM Service (`src/core/llm.py`)

**Purpose**: Generate natural language responses

**Supported Providers**:
- Google Gemini API (gemini-pro)
- OpenAI GPT (gpt-3.5-turbo)

**Key Features**:
- Provider abstraction
- Configurable temperature
- Token limit control
- Prompt templating

### 4. RAG Pipeline (`src/core/rag_pipeline.py`)

**Purpose**: Orchestrate retrieval and generation

**Process**:
1. **Query Reception**: Receive user question
2. **Embedding**: Convert query to vector
3. **Retrieval**: Search vector DB for similar FAQs
4. **Confidence Check**: Evaluate top similarity score
5. **Context Formation**: Format retrieved FAQs as context
6. **Generation**: LLM generates answer from context
7. **Response**: Return answer with citations

**Escalation Logic**:
```python
if no_results or confidence < threshold:
    escalate_to_human()
else:
    generate_llm_answer()
```

### 5. FastAPI Backend (`src/api/main.py`)

**Purpose**: RESTful API server

**Features**:
- Auto-generated OpenAPI docs
- CORS middleware
- Request validation (Pydantic)
- Async support
- Health checks

**Endpoints**:
- `POST /api/v1/query` - Query RAG system
- `POST /api/v1/faq` - Add new FAQ
- `GET /api/v1/metrics` - System metrics
- `GET /health` - Health check

### 6. Streamlit Frontend (`frontend/app.py`)

**Purpose**: Interactive web UI

**Features**:
- Chat interface
- Real-time metrics
- Citation display
- FAQ management
- Session persistence

## Data Flow

### Query Processing Flow

```
1. User Input
   ↓
2. API Endpoint (/api/v1/query)
   ↓
3. RAG Pipeline
   ├─→ Embed Query (EmbeddingService)
   ├─→ Search Vector DB (VectorDatabase)
   ├─→ Check Confidence
   └─→ Generate Answer (LLMService)
   ↓
4. Response + Citations
   ↓
5. Display to User
```

### FAQ Addition Flow

```
1. New FAQ Data
   ↓
2. API Endpoint (/api/v1/faq)
   ↓
3. Create FAQItem
   ↓
4. Generate Embedding
   ↓
5. Add to Vector DB
   ↓
6. Save to Disk
   ↓
7. Return FAQ ID
```

## Performance Considerations

### Latency Breakdown

Typical query processing time (200-400ms):
- Embedding generation: 50-100ms
- Vector search: 10-50ms
- LLM generation: 100-250ms
- Overhead: 10-20ms

### Optimization Strategies

1. **Batch Processing**: Process multiple queries together
2. **Caching**: Cache frequent queries and embeddings
3. **Model Quantization**: Use quantized models for faster inference
4. **Index Optimization**: Use IVF or HNSW indices for large datasets
5. **Async Operations**: Parallelize independent operations

## Scalability

### Current Limitations

- Single-threaded vector search
- In-memory FAISS index
- No distributed processing
- Limited to ~100K FAQs efficiently

### Future Improvements

1. **Distributed Search**: Shard index across multiple nodes
2. **GPU Acceleration**: Use FAISS GPU for faster search
3. **Caching Layer**: Redis for query caching
4. **Load Balancing**: Multiple API instances
5. **Database**: PostgreSQL with pgvector for persistence

## Security

### Current Implementation

- Environment variable configuration
- Input validation (Pydantic)
- CORS configuration
- No authentication (development only)

### Production Recommendations

1. **Authentication**: JWT tokens or API keys
2. **Rate Limiting**: Prevent abuse
3. **HTTPS**: Encrypt data in transit
4. **Input Sanitization**: Prevent injection attacks
5. **Secret Management**: Use vault services
6. **Logging**: Audit trails for all operations

## Monitoring

### Metrics Tracked

- Total queries processed
- Average response latency
- Escalation rate
- Average confidence score
- System uptime
- FAQ database size

### Logging

- Application logs: `logs/app.log`
- Metrics data: `logs/metrics.json`
- Query history with timestamps
- Error tracking and tracing
