import os
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
import httpx
import sys
from pathlib import Path

# Add parent directory to path so we can import from vectordb
sys.path.append(str(Path(__file__).parent.parent))
from vectordb.query import HealthQueryEngine

load_dotenv()

class HalsaVedaChatbot:
    def __init__(self):
        # Initialize OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        http_client = httpx.Client()
        
        self.openai_client = OpenAI(
            api_key=openai_key,
            http_client=http_client
        )
        
        # Initialize RAG query engine
        self.query_engine = HealthQueryEngine()
        
        print("✅ HälsaVeda Chatbot initialized!")
    
    def generate_answer(self, user_question: str, context_chunks: List[Dict]) -> str:
        """
        Generate answer using GPT-4o-mini with retrieved context
        """
        # Format context from chunks
        context = ""
        for i, chunk in enumerate(context_chunks, 1):
            context += f"\n[Source {i}]: {chunk['title']}\n"
            context += f"{chunk['text']}\n"
            context += f"URL: {chunk['url']}\n"
        
        # Create prompt
        system_prompt = """You are HälsaVeda Copilot, an AI assistant helping people navigate Swedish healthcare.

Your role:
- Answer questions about Swedish healthcare clearly and concisely
- Use the provided context from 1177.se (Swedish healthcare website)
- Translate Swedish content to English when needed
- Provide practical, actionable advice
- Always cite your sources with [Source X] references
- If you don't know something, say so

Be empathetic and helpful, especially for immigrants/expats who may find the Swedish system confusing."""

        user_prompt = f"""Question: {user_question}

Context from 1177.se:
{context}

Instructions:
1. Answer the question based on the context above
2. If context is in Swedish, translate key points to English
3. Provide practical steps when relevant
4. Cite sources using [Source 1], [Source 2], etc.
5. If context doesn't fully answer the question, say what you can answer and what's missing

Answer:"""

        # Call GPT-4o-mini
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def chat(self, user_question: str, top_k: int = 3) -> Dict:
        """
        Main chat function - retrieves context and generates answer
        
        Returns:
            {
                'question': user question,
                'answer': generated answer,
                'sources': list of source chunks,
                'metadata': {scores, model, etc}
            }
        """
        print(f"\n🔍 Searching for: {user_question}")
        
        # 1. Retrieve relevant chunks
        chunks = self.query_engine.search(user_question, top_k=top_k)
        
        print(f"✅ Found {len(chunks)} relevant sources")
        
        # 2. Generate answer
        print(f"🤖 Generating answer...")
        answer = self.generate_answer(user_question, chunks)
        
        print(f"✅ Answer generated!")
        
        # 3. Format response
        response = {
            'question': user_question,
            'answer': answer,
            'sources': [
                {
                    'title': chunk['title'],
                    'url': chunk['url'],
                    'score': chunk['score'],
                    'preview': chunk['text'][:200] + '...'
                }
                for chunk in chunks
            ],
            'metadata': {
                'model': 'gpt-4o-mini',
                'num_sources': len(chunks)
            }
        }
        
        return response


if __name__ == "__main__":
    print("="*70)
    print("HÄLSAVEDA CHATBOT - TEST")
    print("="*70)
    
    # Initialize chatbot
    chatbot = HalsaVedaChatbot()
    
    # Test questions
    test_questions = [
        "What should I do if I have a cold?",
        "When should I see a doctor for a fever?",
        "How do I know if I need to go to the emergency room?",
        "Vad ska jag göra om jag har feber?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*70}")
        print(f"❓ USER: {question}")
        print(f"{'='*70}")
        
        # Get response
        response = chatbot.chat(question)
        
        # Display answer
        print(f"\n🤖 ASSISTANT:\n{response['answer']}")
        
        # Display sources
        print(f"\n📚 SOURCES:")
        for i, source in enumerate(response['sources'], 1):
            print(f"   [{i}] {source['title']} (score: {source['score']:.3f})")
            print(f"       {source['url']}")
        
        print("\n" + "="*70)
        input("Press Enter for next question...")
    
    print("\n✅ Chatbot test complete!")
