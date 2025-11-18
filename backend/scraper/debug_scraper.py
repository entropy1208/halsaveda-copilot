import requests
from bs4 import BeautifulSoup

url = "https://www.1177.se/sjukdomar--besvar/infektioner/forkylning-och-influensa/forkylning/"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'html.parser')

print("="*70)
print("DEBUGGING: What are we actually capturing?")
print("="*70)

# Method 1: Current approach (main tag)
main = soup.find('main')
if main:
    current_text = main.get_text(separator=' ', strip=True)
    print(f"\n📦 Current method (main tag):")
    print(f"   Characters: {len(current_text)}")
    print(f"   Preview: {current_text[:300]}...")

# Method 2: All paragraphs
paragraphs = soup.find_all('p')
para_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
print(f"\n📦 All <p> tags:")
print(f"   Characters: {len(para_text)}")
print(f"   Preview: {para_text[:300]}...")

# Method 3: Find article content specifically
article = soup.find('article')
if article:
    article_text = article.get_text(separator=' ', strip=True)
    print(f"\n📦 Article tag:")
    print(f"   Characters: {len(article_text)}")
    print(f"   Preview: {article_text[:300]}...")

# Method 4: Look for specific content divs
content_selectors = [
    'div[class*="content"]',
    'div[class*="article"]',
    'section[class*="body"]',
]

for selector in content_selectors:
    elements = soup.select(selector)
    if elements:
        text = ' '.join([e.get_text(separator=' ', strip=True) for e in elements])
        print(f"\n📦 Selector '{selector}':")
        print(f"   Elements found: {len(elements)}")
        print(f"   Characters: {len(text)}")
        print(f"   Preview: {text[:200]}...")

# Show structure
print(f"\n🏗️  HTML Structure:")
print(f"   Total <p> tags: {len(paragraphs)}")
print(f"   Total <h1> tags: {len(soup.find_all('h1'))}")
print(f"   Total <h2> tags: {len(soup.find_all('h2'))}")
print(f"   Total <h3> tags: {len(soup.find_all('h3'))}")

# Check for sections
sections = soup.find_all(['section', 'div'], class_=lambda x: x and 'section' in x.lower())
print(f"   Section-like elements: {len(sections)}")

print("\n" + "="*70)