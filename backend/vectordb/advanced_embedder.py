import os
import json
from pathlib import Path
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict
import time
from tqdm import tqdm
from dotenv import load_dotenv
import httpx

load_dotenv()

class AdvancedEmbedder:
    """
    Advanced embedder with:
    - Batch processing
    - Progress tracking
    - Error recovery
    - Metadata enrichment
    """
    
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            http_client=httpx.Client(),
            max_retries=2,
            timeout=30.0
        )
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index_name = 'halsaveda-comprehensive'
        self.embedding_model = 'text-embedding-3-small'  # Or use 3-large for better quality
        self.dimension = 1536  # 3-small: 1536, 3-large: 3072
        
    def create_index(self):
        """Create or recreate Pinecone index"""
        # Delete old index if exists
        if self.index_name in [idx.name for idx in self.pc.list_indexes()]:
            print(f"⚠️  Deleting existing index: {self.index_name}")
            self.pc.delete_index(self.index_name)
            time.sleep(5)
        
        # Create new index
        print(f"🔧 Creating index: {self.index_name}")
        self.pc.create_index(
            name=self.index_name,
            dimension=self.dimension,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        
        # Wait for index to be ready
        while not self.pc.describe_index(self.index_name).status['ready']:
            print("  Waiting for index...")
            time.sleep(2)
        
        print("✅ Index ready!")
        return self.pc.Index(self.index_name)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100):
        """Generate embeddings in batches"""
        all_embeddings = []
        
        print(f"📊 Generating embeddings for {len(texts)} chunks...")
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Batches"):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Rate limiting protection
                time.sleep(0.5)
                
            except Exception as e:
                print(f"\n❌ Error in batch {i}-{i+batch_size}: {e}")
                # Retry with smaller batch
                for text in batch:
                    try:
                        response = self.openai_client.embeddings.create(
                            model=self.embedding_model,
                            input=[text]
                        )
                        all_embeddings.append(response.data[0].embedding)
                        time.sleep(1)
                    except Exception as retry_e:
                        print(f"  Failed to embed: {text[:50]}... Error: {retry_e}")
                        all_embeddings.append([0.0] * self.dimension)  # Placeholder
        
        return all_embeddings
    
    def enrich_metadata(self, chunk: Dict) -> Dict:
        """Add metadata for better filtering/search"""
        metadata = chunk.get('metadata', {})
        
        # Extract topic from URL
        url = metadata.get('url', '')
        if 'sjukdomar--besvar' in url:
            metadata['category'] = 'diseases_conditions'
        elif 'barn--gravid' in url:
            metadata['category'] = 'children_pregnancy'
        elif 'liv--hälsa' in url:
            metadata['category'] = 'lifestyle_health'
        elif 'hitta-vard' in url:
            metadata['category'] = 'finding_care'
        else:
            metadata['category'] = 'other'
        
        # Add chunk length
        metadata['chunk_length'] = chunk.get('word_count', 0)
        metadata['chunk_type'] = chunk.get('chunk_type', 'unknown')
        
        # Add heading for better context
        metadata['heading'] = chunk.get('heading', '')[:100]  # Truncate
        
        return metadata
    
    def upload_to_pinecone(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Upload chunks and embeddings to Pinecone"""
        index = self.pc.Index(self.index_name)
        
        # Prepare vectors
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = self.enrich_metadata(chunk)
            
            # Pinecone metadata size limit workaround
            # Store full text separately if needed
            text_preview = chunk['text'][:1000]  # First 1000 chars
            
            vector = {
                'id': f"chunk_{i}",
                'values': embedding,
                'metadata': {
                    **metadata,
                    'text': text_preview,
                    'full_text_length': len(chunk['text'])
                }
            }
            vectors.append(vector)
        
        # Upload in batches
        batch_size = 100
        print(f"\n🔄 Uploading {len(vectors)} vectors to Pinecone...")
        
        for i in tqdm(range(0, len(vectors), batch_size), desc="Upload batches"):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            time.sleep(0.5)
        
        print("✅ Upload complete!")
        
        # Verify
        stats = index.describe_index_stats()
        print(f"\n📊 Pinecone Index Stats:")
        print(f"   Total vectors: {stats.total_vector_count}")
        print(f"   Dimension: {stats.dimension}")
    
    def process_chunks_file(self, chunks_file: str):
        """Main processing pipeline"""
        print("="*70)
        print("ADVANCED EMBEDDING PIPELINE")
        print("="*70)
        
        # Load chunks
        print(f"\n📂 Loading chunks from: {chunks_file}")
        chunks_path = Path(__file__).parent.parent / 'data' / chunks_file
        
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"✅ Loaded {len(chunks)} chunks")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        print(f"\n✅ Generated {len(embeddings)} embeddings")
        
        # Create fresh index
        self.create_index()
        
        # Upload
        self.upload_to_pinecone(chunks, embeddings)
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE!")
        print("="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunks-file', 
                       default='semantic_chunks.json',
                       help='Chunks file to process')
    parser.add_argument('--model',
                       choices=['small', 'large'],
                       default='small',
                       help='Embedding model size')
    
    args = parser.parse_args()
    
    embedder = AdvancedEmbedder()
    
    # Update model if large
    if args.model == 'large':
        embedder.embedding_model = 'text-embedding-3-large'
        embedder.dimension = 3072
        print("Using text-embedding-3-large (higher quality, 3x cost)")
    
    embedder.process_chunks_file(args.chunks_file)
