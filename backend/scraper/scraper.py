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
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "No title"
            
            # Extract main content
            content_div = soup.find('div', class_='article-body') or soup.find('article')
            content_text = content_div.get_text(strip=True) if content_div else "No content"
            
            return {
                'url': url,
                'title': title_text,
                'content': content_text,
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
        
        print(f"Saved to {filepath}")

# Test it!
if __name__ == "__main__":
    scraper = HealthScraper()
    
    # Test URL - Healthcare system overview
    test_url = "https://www.1177.se/liv--halsa/sa-fungerar-kroppen/"
    
    print(f"Scraping: {test_url}")
    result = scraper.scrape_page(test_url)
    
    if result:
        print(f"\nTitle: {result['title']}")
        print(f"Content length: {len(result['content'])} characters")
        print(f"\nFirst 200 chars:\n{result['content'][:200]}...")
        
        scraper.save_to_json([result])
        print("\n✅ SUCCESS! Check data/scraped_data.json")
    else:
        print("❌ Failed to scrape")
