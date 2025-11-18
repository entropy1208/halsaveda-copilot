import json
import os
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import time
import httpx

# Load environment variables
load_dotenv()

class EmbeddingGenerator:
    def __init__(self):
        # Validate API keys first
        openai_key = os.getenv('OPENAI_API_KEY')
        pinecone_key = os.getenv('PINECONE_API_KEY')
        
        if not openai_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file")
        if not pinecone_key:
            raise ValueError("❌ PINECONE_API_KEY not found in .env file")
        
        print("✅ API keys loaded")
       
        try:
            # Create a clean httpx client
            http_client = httpx.Client()
    
            self.openai_client = OpenAI(
                api_key=openai_key,
                http_client=http_client,
                max_retries=2,
                timeout=30.0
            )
            print("✅ OpenAI client initialized")
        except Exception as e:
            raise ValueError(f"❌ Failed to initialize OpenAI client: {e}")

        try:
            self.pc = Pinecone(api_key=pinecone_key)
            print("✅ Pinecone client initialized")
        except Exception as e:
            raise ValueError(f"❌ Failed to initialize Pinecone client: {e}")
        
        self.index_name = 'halsaveda-index'
        self.embedding_model = 'text-embedding-3-small'
        
    def create_pinecone_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print("⏳ Waiting for index to be ready...")
            time.sleep(5)
            print("✅ Index created!")
        else:
            print(f"✅ Index '{self.index_name}' already exists")
        
        return self.pc.Index(self.index_name)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings for all chunks"""
        print(f"\n🔄 Generating embeddings for {len(chunks)} chunks...")
        
        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            if (i + 1) % 5 == 0:
                print(f"  Progress: {i+1}/{len(chunks)}")
            
            embedding = self.generate_embedding(chunk['text'])
            
            if embedding:
                chunk['embedding'] = embedding
                embedded_chunks.append(chunk)
            else:
                print(f"  ⚠️  Skipped chunk {i}")
            
            # Rate limiting
            time.sleep(0.2)
        
        print(f"✅ Generated {len(embedded_chunks)} embeddings")
        return embedded_chunks
    
    def upload_to_pinecone(self, embedded_chunks: List[Dict]):
        """Upload embedded chunks to Pinecone"""
        index = self.create_pinecone_index()
        
        print(f"\n🔄 Uploading {len(embedded_chunks)} vectors to Pinecone...")
        
        # Prepare vectors
        vectors = []
        for i, chunk in enumerate(embedded_chunks):
            vector = {
                'id': f"chunk_{i}_{int(time.time())}",  # Unique ID
                'values': chunk['embedding'],
                'metadata': {
                    'text': chunk['text'][:1000],  # Truncate for Pinecone limits
                    'title': chunk['doc_title'],
                    'url': chunk['doc_url'],
                    'chunk_index': chunk['chunk_index']
                }
            }
            vectors.append(vector)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            try:
                index.upsert(vectors=batch)
                print(f"  ✅ Uploaded batch {i//batch_size + 1}")
            except Exception as e:
                print(f"  ❌ Error uploading batch: {e}")
        
        print("✅ Upload complete!")
        
        # Get stats
        time.sleep(2)  # Wait for indexing
        stats = index.describe_index_stats()
        print(f"\n📊 Pinecone Index Stats:")
        print(f"   Total vectors: {stats.total_vector_count}")
        print(f"   Dimension: {stats.dimension}")

if __name__ == "__main__":
    print("="*70)
    print("EMBEDDING GENERATOR")
    print("="*70)
    
    try:
        # Load chunks
        print("\n📂 Loading chunks...")
        chunks_path = Path(__file__).parent.parent / 'data' / 'semantic_chunks.json'
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"   ✅ Loaded {len(chunks)} chunks")
        
        # Initialize embedder
        print("\n🔧 Initializing embedder...")
        embedder = EmbeddingGenerator()
        
        # Generate embeddings
        print("\n⚡ Generating embeddings...")
        embedded_chunks = embedder.embed_chunks(chunks)
        
        # Save locally
        print("\n💾 Saving embedded chunks...")
        output_path = Path(__file__).parent.parent / 'data' / 'embedded_chunks.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Saved to {output_path}")
        
        # Upload to Pinecone
        print("\n☁️  Uploading to Pinecone...")
        embedder.upload_to_pinecone(embedded_chunks)
        
        print("\n" + "="*70)
        print("🎉 COMPLETE! Your RAG vector database is ready!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
