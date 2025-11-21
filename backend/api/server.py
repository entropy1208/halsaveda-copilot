from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from api.chatbot import HalsaVedaChatbot

# Initialize FastAPI
app = FastAPI(
    title="HälsaVeda Copilot API",
    description="AI-powered Swedish healthcare assistant",
    version="1.0.0"
)

# Enable CORS - MUST BE IMMEDIATELY AFTER APP CREATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://halsaveda.app",
        "https://www.halsaveda.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = None

# Stats file path
STATS_FILE = Path(__file__).parent.parent / 'data' / 'stats.json'


def increment_query_count():
    """Increment and persist query counter"""
    stats = {
        'total_queries': 0,
        'last_updated': None,
        'first_query': None
    }
    
    # Load existing stats
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load stats file: {e}")
    
    # Increment counter
    stats['total_queries'] += 1
    stats['last_updated'] = datetime.now().isoformat()
    
    # Set first query timestamp if not set
    if not stats.get('first_query'):
        stats['first_query'] = datetime.now().isoformat()
    
    # Save stats
    try:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save stats: {e}")
    
    return stats['total_queries']


@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on startup"""
    global chatbot
    print("=" * 70)
    print("🚀 Starting HälsaVeda Copilot API")
    print("=" * 70)
    print("\n🔧 Initializing chatbot...")
    
    try:
        chatbot = HalsaVedaChatbot()
        print("✅ Chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        raise
    
    print("\n" + "=" * 70)
    print("✅ Server ready!")
    print("=" * 70)


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
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "stats": "/api/stats",
            "usage": "/api/stats/usage"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "chatbot_ready": chatbot is not None,
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "stats": "/api/stats",
            "usage": "/api/stats/usage"
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
        raise HTTPException(
            status_code=503, 
            detail="Chatbot not initialized. Please try again in a moment."
        )
    
    # Increment query counter
    try:
        query_count = increment_query_count()
        print(f"📊 Query #{query_count}: {request.question[:50]}...")
    except Exception as e:
        print(f"Warning: Query counter failed: {e}")
        query_count = 0
    
    try:
        # Get response from chatbot
        response = chatbot.chat(request.question, top_k=request.top_k)
        
        # Add query count to metadata
        response['metadata']['query_number'] = query_count
        response['metadata']['timestamp'] = datetime.now().isoformat()
        
        return ChatResponse(
            question=response['question'],
            answer=response['answer'],
            sources=[Source(**source) for source in response['sources']],
            metadata=response['metadata']
        )
    
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not chatbot:
        raise HTTPException(
            status_code=503, 
            detail="Chatbot not initialized"
        )
    
    try:
        # Get Pinecone stats
        stats = chatbot.query_engine.index.describe_index_stats()
        
        # Load query stats
        query_stats = {"total_queries": 0}
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                query_stats = json.load(f)
        
        return {
            "vector_database": {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_name": "halsaveda-index"
            },
            "models": {
                "embedding": "text-embedding-3-small",
                "llm": "gpt-4o-mini"
            },
            "usage": {
                "total_queries": query_stats.get('total_queries', 0),
                "last_updated": query_stats.get('last_updated'),
                "first_query": query_stats.get('first_query')
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )


@app.get("/api/stats/usage")
async def usage_stats():
    """Get public usage statistics (no auth required)"""
    stats = {
        "total_queries": 0,
        "status": "operational",
        "uptime": "online"
    }
    
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                stats["total_queries"] = data.get('total_queries', 0)
                stats["last_query"] = data.get('last_updated')
        except Exception as e:
            print(f"Warning: Could not load usage stats: {e}")
    
    return stats


if __name__ == "__main__":
    import uvicorn
    import os
    
    print("=" * 70)
    print("Starting HälsaVeda Copilot API Server")
    print("=" * 70)
    print("\n📍 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    print("📊 Stats: http://localhost:8000/api/stats")
    print("\n" + "=" * 70)
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
