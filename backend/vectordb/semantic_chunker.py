import json
from pathlib import Path
from typing import List, Dict

class SemanticChunker:
    """
    Smarter chunking that respects document structure
    """
    
    def __init__(self, min_chunk_size=100, max_chunk_size=500):
        self.min_chunk_size = min_chunk_size  # Minimum words
        self.max_chunk_size = max_chunk_size  # Maximum words
    
    def chunk_by_sections(self, document: Dict) -> List[Dict]:
        """
        Chunk based on document sections (headings)
        Each chunk = one section with its heading as context
        """
        chunks = []
        
        if 'structured_content' not in document:
            # Fallback to old method
            return self.fallback_chunk(document)
        
        sections = document['structured_content']['sections']
        
        for section in sections:
            heading = section['heading']
            content_parts = section['content']
            
            # Combine all content in this section
            full_section_text = ' '.join(content_parts)
            
            # If section is too long, split it intelligently
            if self.word_count(full_section_text) > self.max_chunk_size:
                sub_chunks = self.split_long_section(heading, content_parts)
                chunks.extend(sub_chunks)
            else:
                # Keep section as one chunk
                chunk = {
                    'text': f"{heading}. {full_section_text}",
                    'heading': heading,
                    'section_level': section['level'],
                    'word_count': self.word_count(full_section_text),
                    'chunk_type': 'section'
                }
                chunks.append(chunk)
        
        return chunks
    
    def split_long_section(self, heading: str, paragraphs: List[str]) -> List[Dict]:
        """
        Split a long section into multiple chunks by paragraphs
        but keep heading context
        """
        chunks = []
        current_chunk_paras = []
        current_word_count = 0
        
        for para in paragraphs:
            para_words = self.word_count(para)
            
            # If adding this paragraph exceeds max, save current chunk
            if current_word_count + para_words > self.max_chunk_size and current_chunk_paras:
                chunk_text = f"{heading}. {' '.join(current_chunk_paras)}"
                chunks.append({
                    'text': chunk_text,
                    'heading': heading,
                    'word_count': current_word_count,
                    'chunk_type': 'section_part'
                })
                current_chunk_paras = []
                current_word_count = 0
            
            current_chunk_paras.append(para)
            current_word_count += para_words
        
        # Add remaining paragraphs
        if current_chunk_paras:
            chunk_text = f"{heading}. {' '.join(current_chunk_paras)}"
            chunks.append({
                'text': chunk_text,
                'heading': heading,
                'word_count': current_word_count,
                'chunk_type': 'section_part'
            })
        
        return chunks
    
    def word_count(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def fallback_chunk(self, document: Dict) -> List[Dict]:
        """Fallback for documents without structured content"""
        text = document['content']
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.max_chunk_size):
            chunk_words = words[i:i + self.max_chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append({
                'text': chunk_text,
                'heading': 'Content',
                'word_count': len(chunk_words),
                'chunk_type': 'fallback'
            })
        
        return chunks
    
    def process_documents(self, json_file: str) -> List[Dict]:
        """Process all documents with semantic chunking"""
        with open(json_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_by_sections(doc)
            
            # Add document-level metadata
            for i, chunk in enumerate(chunks):
                chunk['chunk_index'] = i
                chunk['doc_title'] = doc['title']
                chunk['doc_url'] = doc['url']
                chunk['metadata'] = {
                    'url': doc['url'],
                    'title': doc['title'],
                    'scraped_at': doc.get('scraped_at', '')
                }
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], output_file='semantic_chunks.json'):
        """Save chunks to file"""
        output_dir = Path('data')
        filepath = output_dir / output_file
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(chunks)} semantic chunks to {filepath}")


if __name__ == "__main__":
    print("="*70)
    print("SEMANTIC CHUNKING")
    print("="*70)
    
    chunker = SemanticChunker(min_chunk_size=100, max_chunk_size=400)
    
    # Use improved scraper data
    print("\n📂 Loading improved scraped data...")
    chunks = chunker.process_documents('data/tier2_top200_scraped_20251122.json')
    
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    
    # Show examples
    print(f"\n📝 Example chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n   Chunk {i+1}:")
        print(f"   Heading: {chunk['heading']}")
        print(f"   Words: {chunk['word_count']}")
        print(f"   Type: {chunk['chunk_type']}")
        print(f"   Text: {chunk['text'][:150]}...")
    
    chunker.save_chunks(chunks)
    
    print("\n" + "="*70)
    print("✅ Semantic chunking complete!")
    print("="*70)
