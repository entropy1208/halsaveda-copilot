import os
from typing import List, Dict
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import httpx

load_dotenv()

class HealthQueryEngine:
    def __init__(self):
        # Clean OpenAI initialization
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        # Create clean HTTP client to avoid proxy issues
        http_client = httpx.Client()
        
        self.openai_client = OpenAI(
            api_key=openai_key,
            http_client=http_client
        )
        self.embedding_model = 'text-embedding-3-small'
        
        # Pinecone
        pinecone_key = os.getenv('PINECONE_API_KEY')
        self.pc = Pinecone(api_key=pinecone_key)
        self.index = self.pc.Index('halsaveda-index')
        
        print("✅ Query engine ready!")
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query using OpenAI"""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        return response.data[0].embedding
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant chunks based on query"""
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        chunks = []
        for match in results['matches']:
            chunk = {
                'text': match['metadata']['text'],
                'title': match['metadata']['title'],
                'url': match['metadata']['url'],
                'score': match['score']
            }
            chunks.append(chunk)
        
        return chunks
    
    def format_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks into context string"""
        context = ""
        for i, chunk in enumerate(chunks, 1):
            context += f"\n--- Source {i}: {chunk['title']} ---\n"
            context += f"{chunk['text']}\n"
            context += f"URL: {chunk['url']}\n"
        return context


if __name__ == "__main__":
    print("="*70)
    print("HEALTHCARE QUERY SYSTEM - TEST")
    print("="*70)
    
    engine = HealthQueryEngine()
    
    test_queries = [
        "Vad ska jag göra om jag är förkyld?",
        "How do I treat a cold?",
        "När ska jag söka vård för feber?",
        "What are common cold symptoms?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"❓ Query: {query}")
        print(f"{'='*70}")
        
        results = engine.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Result {i} (Score: {result['score']:.3f})")
            print(f"   Title: {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Text: {result['text'][:200]}...")
    
    print("\n" + "="*70)
    print("✅ Query system working!")
    print("="*70)
