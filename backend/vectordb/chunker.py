import json
from pathlib import Path
from typing import List, Dict

class TextChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        """
        chunk_size: approximate number of words per chunk
        chunk_overlap: number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks
        """
        # Split into words
        words = text.split()
        chunks = []
        
        # Create overlapping chunks
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk = {
                'text': chunk_text,
                'chunk_index': len(chunks),
                'word_count': len(chunk_words),
                'metadata': metadata or {}
            }
            chunks.append(chunk)
            
            # Stop if we've processed all words
            if i + self.chunk_size >= len(words):
                break
        
        return chunks
    
    def process_documents(self, json_file: str) -> List[Dict]:
        """
        Load scraped documents and chunk them
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        all_chunks = []
        
        for doc in documents:
            # Skip if no real content
            if doc.get('content') == 'Could not extract content':
                continue
            
            # Create metadata
            metadata = {
                'url': doc['url'],
                'title': doc['title'],
                'scraped_at': doc['scraped_at']
            }
            
            # Chunk the document
            chunks = self.chunk_text(doc['content'], metadata)
            
            # Add document-level info
            for chunk in chunks:
                chunk['doc_title'] = doc['title']
                chunk['doc_url'] = doc['url']
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], output_file='chunked_data.json'):
        """Save chunks to file"""
        output_dir = Path('data')
        filepath = output_dir / output_file
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(chunks)} chunks to {filepath}")

if __name__ == "__main__":
    chunker = TextChunker(chunk_size=300, chunk_overlap=50)
    
    print("="*70)
    print("Loading scraped data...")
    chunks = chunker.process_documents('data/scraped_data.json')
    
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    
    # Show example chunks
    print(f"\n📝 Example chunk:")
    if chunks:
        example = chunks[0]
        print(f"   Title: {example['doc_title']}")
        print(f"   URL: {example['doc_url']}")
        print(f"   Words: {example['word_count']}")
        print(f"   Text preview: {example['text'][:200]}...")
    
    chunker.save_chunks(chunks)
    print("="*70)
