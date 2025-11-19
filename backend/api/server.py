from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from api.chatbot import HalsaVedaChatbot

# Initialize FastAPI
app = FastAPI(
    title="HälsaVeda Copilot API",
    description="AI-powered Swedish healthcare assistant",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://halsaveda-copilot-production.up.railway.app",
        "https://*.vercel.app",  # Allow all Vercel preview/production URLs
        "https://halsaveda.app",
        "https://www.halsaveda.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot once at startup
chatbot = None

@app.on_event("startup")
async def startup_event():
    global chatbot
    print("🚀 Initializing HälsaVeda Chatbot...")
    chatbot = HalsaVedaChatbot()
    print("✅ Chatbot ready!")

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class Source(BaseModel):
    title: str
    url: str
    score: float
    preview: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    metadata: Dict

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HälsaVeda Copilot",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "chatbot_ready": chatbot is not None,
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Example:
    POST /api/chat
    {
        "question": "What should I do for a cold?",
        "top_k": 3
    }
    """
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        # Get response from chatbot
        response = chatbot.chat(request.question, top_k=request.top_k)
        
        return ChatResponse(
            question=response['question'],
            answer=response['answer'],
            sources=[Source(**source) for source in response['sources']],
            metadata=response['metadata']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    # Get Pinecone stats
    stats = chatbot.query_engine.index.describe_index_stats()
    
    return {
        "vector_database": {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_name": "halsaveda-index"
        },
        "models": {
            "embedding": "text-embedding-3-small",
            "llm": "gpt-4o-mini"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("Starting HälsaVeda Copilot API Server")
    print("="*70)
    print("\n📍 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    print("\n" + "="*70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
