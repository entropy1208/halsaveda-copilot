import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List

class ImprovedHealthScraper:
    def __init__(self):
        self.base_url = "https://www.1177.se"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_structured_content(self, soup) -> Dict:
        """
        Extract content preserving structure (headings, sections, paragraphs)
        """
        content_parts = []
        
        # Get main content area
        main = soup.find('main') or soup.find('article')
        if not main:
            return {'sections': []}
        
        # Find all headings and content
        elements = main.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol'])
        
        current_section = {
            'heading': 'Introduction',
            'level': 1,
            'content': []
        }
        
        for element in elements:
            tag_name = element.name
            text = element.get_text(strip=True)
            
            if not text:  # Skip empty elements
                continue
            
            # If it's a heading, start new section
            if tag_name in ['h1', 'h2', 'h3', 'h4']:
                # Save previous section if it has content
                if current_section['content']:
                    content_parts.append(current_section)
                
                # Start new section
                level = int(tag_name[1])
                current_section = {
                    'heading': text,
                    'level': level,
                    'content': []
                }
            
            # If it's content, add to current section
            elif tag_name == 'p':
                current_section['content'].append(text)
            
            # If it's a list
            elif tag_name in ['ul', 'ol']:
                items = element.find_all('li')
                list_text = ' '.join([li.get_text(strip=True) for li in items])
                current_section['content'].append(list_text)
        
        # Add last section
        if current_section['content']:
            content_parts.append(current_section)
        
        return {'sections': content_parts}
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape with improved structure preservation"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            
            # Get structured content
            structured_content = self.extract_structured_content(soup)
            
            # Create full text (for backward compatibility)
            full_text_parts = []
            for section in structured_content['sections']:
                full_text_parts.append(f"{section['heading']}: {' '.join(section['content'])}")
            full_text = ' '.join(full_text_parts)
            
            return {
                'url': url,
                'title': title,
                'content': full_text,
                'structured_content': structured_content,
                'content_length': len(full_text),
                'num_sections': len(structured_content['sections']),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_to_json(self, data: List[Dict], filename='improved_scraped_data.json'):
        """Save scraped data"""
        output_dir = Path('data')
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to {filepath}")


if __name__ == "__main__":
    scraper = ImprovedHealthScraper()
    
    urls = [
        "https://www.1177.se/sjukdomar--besvar/infektioner/forkylning-och-influensa/forkylning/",
        "https://www.1177.se/sjukdomar--besvar/infektioner/forkylning-och-influensa/influensa/",
        "https://www.1177.se/hitta-vard/",
    ]
    
    results = []
    
    print("="*70)
    print("IMPROVED SCRAPER - Preserving Structure")
    print("="*70)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Scraping: {url}")
        result = scraper.scrape_page(url)
        
        if result:
            print(f"  ✅ Title: {result['title']}")
            print(f"  📄 Content: {result['content_length']} characters")
            print(f"  📑 Sections: {result['num_sections']}")
            results.append(result)
        
        time.sleep(1)
    
    if results:
        scraper.save_to_json(results)
        print(f"\n🎉 Scraped {len(results)} pages with improved structure!")

print("="*70)