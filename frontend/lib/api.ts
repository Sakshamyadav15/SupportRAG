/**
 * Typed API client for the SupportRAG FastAPI backend.
 * All requests go through Next.js /api/* rewrite → localhost:8000
 */

export interface Citation {
  rank: number
  content: string
  similarity: number
  source: string
  category: string
  resolution_status?: string | null
}

export interface QueryResponse {
  answer: string
  source: string
  confidence: number
  citations: Citation[]
  latency_ms: number
  query: string
  timestamp: string
}

export interface HealthResponse {
  status: string
  faq_store_loaded: boolean
  ticket_store_loaded: boolean
  faq_threshold: number
}

export interface StatsResponse {
  total_queries: number
  avg_latency_ms: number
  avg_confidence: number
  source_breakdown: Record<string, number>
}

const BASE = "/api"

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export async function queryRAG(question: string, top_k = 3): Promise<QueryResponse> {
  return request<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ question, top_k }),
  })
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health")
}

export async function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/stats")
}
