import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

class HealthScraper:
    def __init__(self):
        self.base_url = "https://www.1177.se"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_page(self, url):
        """Scrape a single page from 1177"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "No title"
            
            # Try multiple selectors to find content
            content_text = None
            
            # Strategy 1: Find main content area
            selectors_to_try = [
                ('main', None),
                ('article', None),
                ('div', {'role': 'main'}),
                ('div', {'class': 'content'}),
                ('div', {'id': 'content'}),
            ]
            
            for tag, attrs in selectors_to_try:
                if attrs:
                    content_div = soup.find(tag, attrs)
                else:
                    content_div = soup.find(tag)
                    
                if content_div:
                    # Get all text, clean it up
                    text = content_div.get_text(separator=' ', strip=True)
                    # Remove excessive whitespace
                    text = ' '.join(text.split())
                    if len(text) > 100:  # Only accept if substantial content
                        content_text = text
                        break
            
            # Fallback: get all paragraphs
            if not content_text or len(content_text) < 100:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    texts = [p.get_text(strip=True) for p in paragraphs]
                    content_text = ' '.join(texts)
                    content_text = ' '.join(content_text.split())
            
            if not content_text or len(content_text) < 50:
                content_text = "Could not extract content"
            
            return {
                'url': url,
                'title': title_text,
                'content': content_text,
                'content_length': len(content_text),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def save_to_json(self, data, filename='scraped_data.json'):
        """Save scraped data to JSON file"""
        output_dir = Path('data')
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to {filepath}")

if __name__ == "__main__":
    scraper = HealthScraper()
    
    # URLs to scrape - verified working
    urls = [
        "https://www.1177.se/sjukdomar--besvar/infektioner/forkylning-och-influensa/forkylning/",
        "https://www.1177.se/sjukdomar--besvar/infektioner/forkylning-och-influensa/influensa/",
        "https://www.1177.se/sjukdomar--besvar/mage-och-tarm/diarrhea/diarr/",
        "https://www.1177.se/sjukdomar--besvar/huvud-och-ansikte/huvudvark/huvudvark/",
        "https://www.1177.se/hitta-vard/",
    ]
    
    results = []
    
    print("="*70)
    print("Starting scraper...")
    print("="*70)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Scraping: {url}")
        result = scraper.scrape_page(url)
        
        if result and result['content'] != "Could not extract content":
            print(f"  ✅ Title: {result['title']}")
            print(f"  📄 Content: {result['content_length']} characters")
            print(f"  📝 Preview: {result['content'][:150]}...")
            results.append(result)
        else:
            print(f"  ❌ Failed or no content")
        
        time.sleep(1)  # Be polite
    
    print("\n" + "="*70)
    if results:
        scraper.save_to_json(results)
        print(f"🎉 SUCCESS! Scraped {len(results)}/{len(urls)} pages")
        print(f"📁 Check data/scraped_data.json")
    else:
        print("❌ No pages scraped successfully")
    print("="*70)
