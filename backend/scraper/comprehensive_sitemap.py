import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import time
from collections import defaultdict
import re

class ComprehensiveScraper:
    def __init__(self):
        self.base_url = "https://www.1177.se"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.discovered_urls = set()
    
    def get_sitemap_urls(self):
        """Try to get URLs from sitemap first"""
        sitemap_locations = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-index.xml',
            '/robots.txt'  # Check robots.txt for sitemap location
        ]
        
        for location in sitemap_locations:
            try:
                url = self.base_url + location
                print(f"Checking: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    if location.endswith('.txt'):
                        # Parse robots.txt
                        for line in response.text.split('\n'):
                            if 'Sitemap:' in line:
                                sitemap_url = line.split('Sitemap:')[1].strip()
                                return self.parse_sitemap(sitemap_url)
                    else:
                        # Parse XML sitemap
                        return self.parse_sitemap(url)
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        
        return None
    
    def parse_sitemap(self, sitemap_url):
        """Parse XML sitemap"""
        try:
            print(f"📥 Parsing sitemap: {sitemap_url}")
            response = requests.get(sitemap_url, headers=self.headers, timeout=10)
            root = ET.fromstring(response.content)
            
            urls = []
            
            # Check if this is a sitemap index
            sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
            if sitemaps:
                print(f"  Found sitemap index with {len(sitemaps)} sitemaps")
                for sitemap in sitemaps:
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        sub_urls = self.parse_sitemap(loc.text)
                        urls.extend(sub_urls)
            else:
                # Parse URL entries
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    urls.append(url.text)
            
            print(f"  ✅ Found {len(urls)} URLs")
            return urls
            
        except Exception as e:
            print(f"  ❌ Error parsing sitemap: {e}")
            return []
    
    def crawl_main_sections(self):
        """Crawl main sections if sitemap fails"""
        print("\n🕷️ Crawling main sections...")
        
        main_sections = [
            '/sjukdomar--besvar/',
            '/barn--gravid/',
            '/liv--hälsa/',
            '/hitta-vard/',
            '/behandling--hjalpmedel/'
        ]
        
        discovered = set()
        
        for section in main_sections:
            url = self.base_url + section
            print(f"\n📂 Crawling: {url}")
            
            try:
                discovered.update(self.crawl_section(url, depth=3))
                print(f"  Found {len(discovered)} total URLs")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return list(discovered)
    
    def crawl_section(self, url, depth=2):
        """Recursively crawl a section"""
        if depth == 0:
            return set()
        
        discovered = set()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Make absolute URL
                if href.startswith('/'):
                    full_url = self.base_url + href
                else:
                    full_url = href
                
                # Only keep relevant URLs
                if self.is_healthcare_url(full_url):
                    discovered.add(full_url)
            
            time.sleep(0.5)  # Be polite
            
        except Exception as e:
            print(f"    Error crawling {url}: {e}")
        
        return discovered
    
    def is_healthcare_url(self, url):
        """Check if URL is a healthcare content page"""
        if not url.startswith(self.base_url):
            return False
        
        # Include patterns
        include = [
            '/sjukdomar--besvar/',
            '/barn--gravid/',
            '/liv--hälsa/',
            '/hitta-vard/',
            '/behandling--hjalpmedel/'
        ]
        
        # Exclude patterns
        exclude = [
            '/service/',
            '/om-1177/',
            '/globalassets/',
            '/search',
            '/sok',
            '/logga-in',
            '/login',
            '.pdf',
            '.jpg',
            '.png'
        ]
        
        # Must include one of the healthcare patterns
        if not any(pattern in url for pattern in include):
            return False
        
        # Must not include any exclude patterns
        if any(pattern in url.lower() for pattern in exclude):
            return False
        
        # Must have reasonable depth (actual article, not just category)
        path_parts = url.replace(self.base_url, '').strip('/').split('/')
        if len(path_parts) < 2:  # Too shallow
            return False
        
        return True
    
    def categorize_urls(self, urls):
        """Categorize URLs by topic and importance"""
        categories = defaultdict(list)
        
        for url in urls:
            # Extract category from URL structure
            path = url.replace(self.base_url, '')
            parts = path.strip('/').split('/')
            
            if len(parts) >= 2:
                main_cat = parts[0]
                sub_cat = parts[1] if len(parts) > 1 else 'general'
                
                categories[f"{main_cat}/{sub_cat}"].append(url)
        
        return categories
    
    def prioritize_urls(self, urls):
        """Prioritize URLs by importance"""
        
        # High priority keywords
        high_priority = [
            'forkylning', 'influensa', 'covid', 'feber',
            'magsjuka', 'huvudvärk', 'halsont', 
            'depression', 'angest', 'stress',
            'graviditet', 'barn', 'vaccination',
            'diabetes', 'hjartinfarkt', 'blodtryck',
            'cancer', 'astma', 'allergi'
        ]
        
        # Medium priority
        medium_priority = [
            'tandvärk', 'öroninflammation', 'urinvägsinfektion',
            'eksem', 'artros', 'migrän', 'sömnsvårigheter'
        ]
        
        scored_urls = []
        
        for url in urls:
            score = 0
            url_lower = url.lower()
            
            # High priority match
            for keyword in high_priority:
                if keyword in url_lower:
                    score += 10
            
            # Medium priority match
            for keyword in medium_priority:
                if keyword in url_lower:
                    score += 5
            
            # Prefer shorter URLs (more general/important topics)
            path_depth = url.count('/')
            score -= (path_depth - 4) * 2  # Penalize very deep URLs
            
            scored_urls.append((score, url))
        
        # Sort by score (highest first)
        scored_urls.sort(reverse=True, key=lambda x: x[0])
        
        return [url for score, url in scored_urls]


def main():
    print("="*70)
    print("COMPREHENSIVE 1177.SE URL DISCOVERY")
    print("="*70)
    
    scraper = ComprehensiveScraper()
    
    # Try sitemap first
    print("\n📥 Step 1: Checking for sitemap...")
    sitemap_urls = scraper.get_sitemap_urls()
    
    if sitemap_urls:
        print(f"✅ Found {len(sitemap_urls)} URLs in sitemap(s)")
        all_urls = sitemap_urls
    else:
        print("⚠️  No sitemap found, using web crawling...")
        all_urls = scraper.crawl_main_sections()
    
    # Filter to healthcare content only
    print(f"\n🔍 Step 2: Filtering healthcare content...")
    healthcare_urls = [url for url in all_urls if scraper.is_healthcare_url(url)]
    print(f"✅ Found {len(healthcare_urls)} healthcare articles")
    
    # Categorize
    print(f"\n📂 Step 3: Categorizing...")
    categories = scraper.categorize_urls(healthcare_urls)
    
    print(f"\n📊 Categories found: {len(categories)}")
    for cat, urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        print(f"  {cat:40s}: {len(urls):4d} articles")
    
    # Prioritize
    print(f"\n🎯 Step 4: Prioritizing by importance...")
    prioritized_urls = scraper.prioritize_urls(healthcare_urls)
    
    # Save different tiers
    tiers = {
        'tier1_top100.py': prioritized_urls[:100],
        'tier2_top200.py': prioritized_urls[:200],
        'tier3_comprehensive.py': prioritized_urls[:500] if len(prioritized_urls) > 500 else prioritized_urls,
        'all_urls.py': prioritized_urls
    }
    
    for filename, urls in tiers.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'# Auto-generated 1177.se URLs - {len(urls)} pages\n')
            f.write(f'# Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            f.write('URLS = [\n')
            for url in urls:
                f.write(f'    "{url}",\n')
            f.write(']\n')
        
        print(f"✅ Saved {len(urls):4d} URLs to {filename}")
    
    print("\n" + "="*70)
    print(f"🎉 Discovery complete!")
    print(f"   Total healthcare URLs: {len(healthcare_urls)}")
    print(f"   Top 100: tier1_top100.py")
    print(f"   Top 200: tier2_top200.py")
    print(f"   Top 500: tier3_comprehensive.py")
    print(f"   All: all_urls.py")
    print("="*70)
    
    return prioritized_urls


if __name__ == "__main__":
    main()
