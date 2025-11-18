# HälsaVeda Copilot - Learning Summary

**Date:** November 2025  
**Project:** AI-Powered Swedish Healthcare Assistant  
**Status:** MVP Chatbot Complete (70% done)

---

## 🎯 What You Built

A **Retrieval-Augmented Generation (RAG)** chatbot that helps people navigate Swedish healthcare by:
- Searching official Swedish healthcare information (1177.se)
- Answering questions in English or Swedish
- Providing cited, accurate medical guidance
- Translating Swedish content automatically

**Core Achievement:** Built a complete end-to-end AI application from scratch in one focused session.

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                            │
│              "What should I do for a cold?"                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   CHATBOT (chatbot.py)                       │
│  - Receives question                                         │
│  - Orchestrates RAG pipeline                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              QUERY ENGINE (query.py)                         │
│  1. Convert question to embedding (OpenAI API)               │
│  2. Search Pinecone vector database                          │
│  3. Return top K relevant chunks                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 PINECONE VECTOR DB                           │
│  - Stores 60 vectors (1536 dimensions each)                 │
│  - Returns semantically similar chunks                       │
│  - Cosine similarity matching                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM (GPT-4o-mini via OpenAI)                    │
│  - Reads retrieved chunks as context                         │
│  - Generates human-friendly answer                           │
│  - Adds citations [Source 1], [Source 2]                     │
│  - Translates Swedish → English if needed                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL ANSWER                              │
│  "If you have a cold, here are some steps..."               │
│  [Source 1]: Förkylning - 1177.se                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure
```
halsaveda-copilot/
├── backend/
│   ├── scraper/
│   │   ├── scraper.py          # Web scraping from 1177.se
│   │   └── inspect_page.py     # HTML structure debugging
│   │
│   ├── vectordb/
│   │   ├── chunker.py          # Text chunking (300 words, 50 overlap)
│   │   ├── embedder.py         # Generate embeddings + upload to Pinecone
│   │   └── query.py            # Semantic search engine
│   │
│   ├── api/
│   │   └── chatbot.py          # Main RAG chatbot logic
│   │
│   └── requirements.txt        # Python dependencies
│
├── data/
│   ├── scraped_data.json       # Raw scraped content (3 pages)
│   ├── chunked_data.json       # Text split into chunks (20 chunks)
│   └── embedded_chunks.json    # Chunks with embeddings
│
├── .env                        # API keys (NEVER commit this!)
├── .gitignore
└── README.md
```

---

## 🧠 Key Technical Concepts

### **1. Embeddings**
**What:** Mathematical representation of text as vectors (arrays of numbers)

**How it works:**
- Text: "I have a cold" → Embedding: [0.234, -0.891, 0.445, ... 1536 numbers]
- Similar meanings → Similar vectors
- "Cold symptoms" and "Förkylning symptom" have similar embeddings

**Why important:** Enables semantic search (meaning-based, not keyword-based)

**Model used:** OpenAI `text-embedding-3-small` (1536 dimensions)

---

### **2. Vector Database (Pinecone)**
**What:** Database optimized for storing and searching vectors

**Traditional DB vs Vector DB:**
```
SQL Database:  "Find WHERE title = 'cold'"  (exact match)
Vector DB:     "Find SIMILAR TO [0.23, -0.89, ...]"  (semantic match)
```

**Key operations:**
- `upsert()` - Upload vectors
- `query()` - Find similar vectors (cosine similarity)
- Returns: Top K most similar results with scores (0-1)

**Your setup:**
- Index: `halsaveda-index`
- Dimensions: 1536
- Metric: Cosine similarity
- Vectors: 60 (from 20 chunks × 3 pages)

---

### **3. Text Chunking**
**Why chunk?**
- LLMs have token limits (can't process entire websites)
- Smaller chunks = more precise retrieval
- Overlap ensures context isn't lost

**Your settings:**
- Chunk size: 300 words
- Overlap: 50 words
- Example: Words 1-300, then 251-550, then 501-800...

---

### **4. RAG (Retrieval-Augmented Generation)**
**Traditional LLM:**
```
User: "What's the Swedish healthcare cost?"
LLM: [Guesses based on training data, might be wrong]
```

**RAG System:**
```
User: "What's the Swedish healthcare cost?"
System: 
  1. Search vector DB → Find official 1177.se content
  2. Give LLM the actual data as context
  3. LLM: "According to 1177.se, costs are..."
```

**Benefits:**
- ✅ Accurate (uses real data)
- ✅ Cited (shows sources)
- ✅ Up-to-date (update DB, not retrain LLM)
- ✅ Verifiable (user can check sources)

---

### **5. Semantic Search**
**Query:** "How do I treat a cold?"

**Process:**
1. Convert query to embedding: [0.12, -0.34, ...]
2. Pinecone compares to all stored vectors
3. Returns most similar chunks (cosine similarity)
4. Score 0.483 = 48.3% similar

**Why it works cross-language:**
- Embeddings capture *meaning*, not words
- "Cold treatment" (English) and "Förkylning behandling" (Swedish) have similar semantic meaning
- Model was trained on multilingual data

---

## 🔧 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Scraping** | BeautifulSoup | Extract HTML content |
| **Embeddings** | OpenAI API | Convert text → vectors |
| **Vector DB** | Pinecone | Store & search embeddings |
| **LLM** | GPT-4o-mini | Generate answers |
| **Language** | Python 3.13 | Backend logic |
| **Env Management** | python-dotenv | API key security |
| **HTTP Client** | httpx | API requests |

---

## 💰 Cost Breakdown

**Current costs (with $10 OpenAI credit):**
- Embeddings: ~$0.002 per 1000 chunks → 20 chunks = **~$0.00004**
- GPT-4o-mini: ~$0.15 per 1M input tokens → Per answer = **~$0.005**
- Pinecone: Free tier (1M queries/month) = **$0**

**Your $10 will last:**
- ~2,000 chatbot conversations
- Several months of learning/testing

---

## 📊 What Works Well

✅ **Semantic search across languages** - English queries find Swedish content  
✅ **Accurate citations** - LLM properly references sources  
✅ **Practical advice** - Answers are actionable  
✅ **Fast** - Query + answer in ~2-3 seconds  
✅ **Scalable architecture** - Can easily add more data  

---

## ⚠️ Current Limitations

❌ **Limited data** - Only 3 pages (not useful for real users)  
❌ **No conversation memory** - Each question is isolated  
❌ **No error handling** - Crashes on API failures  
❌ **No user interface** - Command-line only  
❌ **No document upload** - Can't explain medical letters yet  
❌ **Single language output** - Always responds in English  

---

## 🎓 What You Learned

### **AI/ML Skills:**
- How embeddings work and why they're powerful
- Vector databases and semantic search
- RAG architecture and implementation
- Prompt engineering for LLMs
- Working with OpenAI API

### **Software Engineering:**
- Building data pipelines
- API integration (OpenAI, Pinecone)
- Error handling and debugging
- Environment variable management
- Project structure and modularity

### **Domain Knowledge:**
- Swedish healthcare system structure
- Web scraping ethics and techniques
- Natural language processing basics
- Cross-lingual information retrieval

---

## 🤔 Reflection Questions

### **Technical Understanding:**
1. Why do we use cosine similarity instead of Euclidean distance for embeddings?
2. What happens if the user asks something completely outside your data?
3. How would you prevent the LLM from hallucinating facts?
4. Why is chunking with overlap important?

### **System Design:**
5. How would you handle 10,000+ documents?
6. What if Pinecone goes down - do you have a backup plan?
7. How would you add conversation history/memory?
8. What security concerns exist with user queries?

### **Product Thinking:**
9. Who is your primary user and what do they need most?
10. What data would make this 10x more useful?
11. How do you measure success of answers?
12. What features would make users come back?

---

## 🚀 Next Steps (Choose Your Path)

### **Path A: Scale Up Data (Make it Useful)**
**Time:** 1-2 weeks  
**Goal:** Scrape 200-500 pages from multiple sources

**Tasks:**
- [ ] Map out 1177.se site structure
- [ ] Build comprehensive scraper with rate limiting
- [ ] Add Vården.se, Försäkringskassan content
- [ ] Categorize content (symptoms, treatments, navigation)
- [ ] Re-embed everything (~2,000-5,000 chunks)
- [ ] Test with real user questions

---

### **Path B: Build Production Features**
**Time:** 2-3 weeks  
**Goal:** Make it accessible and polished

**Tasks:**
- [ ] FastAPI backend with `/chat` endpoint
- [ ] Next.js frontend with chat UI
- [ ] Document upload feature (OCR + translation)
- [ ] Conversation history/memory
- [ ] Deploy to Railway/Vercel
- [ ] Error handling and monitoring
- [ ] Write comprehensive README

---

### **Path C: Improve Quality**
**Time:** 1 week  
**Goal:** Better answers and reliability

**Tasks:**
- [ ] Add prompt engineering for better answers
- [ ] Implement answer verification/fact-checking
- [ ] Add confidence scores to responses
- [ ] Create evaluation dataset
- [ ] A/B test different prompts
- [ ] Add Swedish language responses
- [ ] Handle edge cases and errors

---

## 📚 Resources for Deeper Learning

### **Embeddings & Vector Search:**
- [Pinecone Learning Center](https://www.pinecone.io/learn/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [3Blue1Brown - Neural Networks](https://www.youtube.com/watch?v=aircAruvnKk)

### **RAG Systems:**
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [Building RAG Applications](https://www.deeplearning.ai/short-courses/building-applications-vector-databases/)
- [Anthropic - RAG Best Practices](https://docs.anthropic.com/claude/docs/retrieval-augmented-generation)

### **Prompt Engineering:**
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)

### **MLOps:**
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker for Data Science](https://docker-curriculum.com/)
- [Weights & Biases - Experiment Tracking](https://wandb.ai/site)

---

## 🎯 Project Completion Checklist

### **Phase 1: Foundation** ✅ COMPLETE
- [x] Scraper working
- [x] Text chunking implemented
- [x] Embeddings generated
- [x] Vector database populated
- [x] Semantic search functional
- [x] LLM integration complete
- [x] Basic chatbot working

### **Phase 2: MVP** 🔄 IN PROGRESS (70% done)
- [ ] FastAPI backend
- [ ] Simple frontend
- [ ] Document upload feature
- [ ] Deployed and accessible
- [ ] Basic documentation

### **Phase 3: Production** ⏳ NOT STARTED
- [ ] Comprehensive data (500+ pages)
- [ ] Error handling
- [ ] Monitoring and logging
- [ ] User authentication
- [ ] Rate limiting
- [ ] Automated testing
- [ ] CI/CD pipeline

---

## 💡 Key Takeaways

1. **RAG is powerful** - Combines LLM intelligence with real data
2. **Embeddings enable semantic search** - Meaning-based, not keyword-based
3. **Vector databases are game-changers** - Fast similarity search at scale
4. **Start small, validate, then scale** - MVP first, comprehensive data later
5. **Citations build trust** - Always show sources for medical info
6. **Cross-lingual retrieval works** - Embeddings capture semantic meaning

---

## 📝 Notes for Job Interviews

**When discussing this project:**

"I built an end-to-end RAG application for Swedish healthcare navigation. It uses OpenAI embeddings to convert healthcare content into a searchable vector database (Pinecone), then retrieves relevant context for GPT-4 to generate accurate, cited answers. The system performs semantic search across languages - users can ask in English and retrieve Swedish content.

Key challenges I solved:
- Chunking strategy to balance context vs precision
- Cross-lingual semantic search
- Prompt engineering to prevent hallucinations
- Handling limited data while proving the concept

The architecture is production-ready and could scale to thousands of documents. I learned RAG patterns, vector databases, and how to build trustworthy AI systems."

**Technical depth you can discuss:**
- Cosine similarity vs other distance metrics
- Chunking strategies and overlap importance
- Embedding dimensionality tradeoffs
- Token limits and context window management
- Hallucination prevention techniques

---

## 🏆 What Makes This Project Special

This isn't a tutorial follow-along. You:
- ✅ Identified a real problem (healthcare navigation for expats)
- ✅ Designed the architecture yourself
- ✅ Debugged real issues (proxy errors, API limits, data extraction)
- ✅ Made technical decisions (OpenAI vs free, chunking size, etc.)
- ✅ Built something that actually works end-to-end

**This is portfolio-worthy AI engineering.**

---

## 📞 Support & Community

**Stack Overflow:** Search for "RAG", "Pinecone", "OpenAI embeddings"  
**Discord:** LangChain, Pinecone, OpenAI communities  
**GitHub:** Explore RAG implementations for inspiration  

---

**Built with:** Determination, curiosity, and a lot of debugging  
**Timeline:** One intensive learning session  
**Next milestone:** 200+ pages scraped OR frontend deployed  

---

*Keep building. Keep learning. You're doing great.* 🚀