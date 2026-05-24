# HälsaVeda Copilot - Technical Architecture

## System Overview
```
User Query
    ↓
Frontend (Next.js/Vercel)
    ↓
Backend API (FastAPI/Railway)
    ↓
Query Processing
    ↓
Vector Search (Pinecone)
    ↓
Context Assembly
    ↓
LLM Generation (OpenAI GPT-4o-mini)
    ↓
Response + Citations
```

## Data Pipeline

### 1. Web Scraping
- **Source:** 1177.se (Swedish healthcare portal)
- **Method:** BeautifulSoup4 + Requests
- **Output:** 200 JSON documents with metadata

### 2. Semantic Chunking
- **Strategy:** Preserve heading structure
- **Chunk Size:** 200-800 words (adaptive)
- **Overlap:** 50 words between chunks
- **Output:** ~2,000 semantic chunks

### 3. Embedding Generation
- **Model:** text-embedding-3-small (OpenAI)
- **Dimension:** 1536
- **Batch Size:** 100 chunks
- **Cost:** ~$0.60 for 2,000 chunks

### 4. Vector Storage
- **Database:** Pinecone (serverless)
- **Metric:** Cosine similarity
- **Index:** halsaveda-comprehensive
- **Metadata:** URL, title, heading, category

## API Architecture

### Endpoints

**Health Check:**
```
GET /health
Returns: Service status
```

**Chat:**
```
POST /api/chat
Body: { "question": "...", "top_k": 3 }
Returns: { "answer": "...", "sources": [...] }
```

**Statistics:**
```
GET /api/stats/usage
Returns: { "total_queries": 127, "status": "operational" }
```

### Query Processing Flow

1. **Input Validation** - Check query length, sanitize
2. **Embedding Generation** - Convert query to vector
3. **Vector Search** - Query Pinecone (top-k=3-5)
4. **Context Assembly** - Combine retrieved chunks
5. **Prompt Construction** - Format for GPT-4o-mini
6. **LLM Generation** - Generate answer with citations
7. **Response Formatting** - Structure with sources
8. **Analytics Logging** - Track query count

## Frontend Architecture

### Components
- **ChatInterface** - Main conversation UI
- **MessageBubble** - Individual message display
- **SourceCitations** - Clickable source links
- **ExampleQuestions** - Quick-start queries
- **QueryCounter** - Live usage stats

### State Management
- React hooks (useState, useEffect)
- Local state (no Redux needed for MVP)
- Session storage for chat history

## Deployment

### Backend (Railway)
- **Auto-deploy:** Push to main branch
- **Environment:** Python 3.11
- **Region:** US East
- **Scaling:** Vertical (CPU/Memory)

### Frontend (Vercel)
- **Auto-deploy:** Push to main branch
- **Framework:** Next.js 14
- **Region:** Global CDN
- **Build:** Automatic optimization

## Performance Considerations

### Latency Budget
- Vector search: <100ms
- LLM generation: <1500ms
- Network: <400ms
- **Total: <2000ms**

### Cost Analysis (per 1000 queries)
- Vector search: FREE (Pinecone free tier)
- LLM generation: $2-3 (GPT-4o-mini)
- **Total: ~$2-3 per 1000 queries**

### Scaling Strategy
- **Current:** Single instance (handles ~100 concurrent users)
- **Phase 2:** Horizontal scaling with load balancer
- **Phase 3:** Caching layer for common queries

## Security

- **API Keys:** Environment variables only
- **CORS:** Restricted to frontend domain
- **Rate Limiting:** 100 requests/hour per IP
- **Input Sanitization:** XSS prevention
- **No PII Storage:** Queries logged without user info

## Monitoring

- **Health Checks:** Every 5 minutes
- **Error Tracking:** FastAPI exception handling
- **Query Analytics:** JSON log files
- **Uptime:** Railway dashboard

## Future Improvements

### Phase 2 (Week 2)
- [ ] Cohere re-ranking
- [ ] Hybrid search (vector + BM25)
- [ ] Response caching

### Phase 3 (Month 2)
- [ ] User authentication
- [ ] Conversation persistence
- [ ] A/B testing framework
- [ ] Content auto-updates
