# SupportRAG API Documentation

## Overview

SupportRAG provides a RESTful API for retrieval-augmented generation powered question answering. The API is built with FastAPI and includes automatic OpenAPI documentation.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Currently, the API does not require authentication. In production, consider adding:
- API key authentication
- OAuth2
- Rate limiting

## Endpoints

### Health Check

Check system health and component status.

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-03T12:00:00.000Z",
  "checks": {
    "vector_db": true,
    "llm": true
  }
}
```

### Query RAG System

Submit a question and receive an AI-generated answer with citations.

**POST** `/api/v1/query`

**Request Body:**
```json
{
  "question": "How do I reset my password?",
  "top_k": 3,
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "answer": "To reset your password, go to the login page...",
  "citations": [
    {
      "faq_id": "faq_00001",
      "question": "How do I reset my password?",
      "answer": "Go to the login page and click...",
      "similarity_score": 0.95,
      "category": "account"
    }
  ],
  "confidence_score": 0.95,
  "escalated": false,
  "latency_ms": 145.2,
  "query_id": "uuid-here",
  "timestamp": "2025-10-03T12:00:00.000Z"
}
```

### Add FAQ

Add a new FAQ to the knowledge base.

**POST** `/api/v1/faq`

**Request Body:**
```json
{
  "question": "What is your return policy?",
  "answer": "We offer 30-day returns...",
  "category": "returns",
  "tags": ["returns", "policy"]
}
```

**Response:**
```json
{
  "success": true,
  "faq_id": "faq_00021",
  "message": "FAQ added successfully"
}
```

### Get Metrics

Retrieve system performance metrics.

**GET** `/api/v1/metrics`

**Response:**
```json
{
  "total_queries": 1523,
  "escalation_rate": 12.5,
  "average_latency_ms": 156.3,
  "average_confidence": 0.87,
  "total_faqs": 250,
  "uptime_seconds": 86400
}
```

## Error Responses

All endpoints follow standard HTTP status codes:

- `200`: Success
- `400`: Bad Request
- `422`: Validation Error
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently not implemented. Recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per user

## Examples

### Python

```python
import requests

# Query the RAG system
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "How do I reset my password?",
        "top_k": 3
    }
)
result = response.json()
print(result["answer"])
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 3}'
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'How do I reset my password?',
    top_k: 3
  })
});
const result = await response.json();
console.log(result.answer);
```

## Best Practices

1. **Always handle errors**: Check response status codes
2. **Use top_k wisely**: 3-5 is usually optimal
3. **Monitor latency**: Track response times for performance
4. **Handle escalations**: Check the `escalated` field in responses
5. **Validate input**: Ensure questions are non-empty and meaningful
