import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import time

def get_page_content(url):
    """Fetch and extract main content from a page"""
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get main content
        main = soup.find('main') or soup.find('article')
        if main:
            # Get title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else ""
            
            # Get body text
            body_text = main.get_text(separator=' ', strip=True)
            
            return {
                'title': title_text,
                'body': body_text,
                'length': len(body_text)
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def similarity_ratio(text1, text2):
    """Calculate similarity between two texts"""
    return SequenceMatcher(None, text1, text2).ratio()


def compare_regional_vs_national():
    """Compare regional URLs vs potential national equivalents"""
    
    # Test cases - pairs of regional and potential national URLs
    test_cases = [
        {
            'regional': 'https://www.1177.se/Vastmanland/barn--gravid/graviditet/graviditet-arbete-och-miljo2/',
            'national_guess': 'https://www.1177.se/barn--gravid/graviditet/livsstil-och-halsa-under-graviditeten/graviditet-och-arbete/',
            'topic': 'Pregnancy and work'
        },
        {
            'regional': 'https://www.1177.se/Ostergotland/barn--gravid/graviditet/graviditetsbesvar-och-sjukdomar/mellanmal-frukt-och-gronsaker-vid-graviditetsdiabetes/',
            'national_guess': 'https://www.1177.se/barn--gravid/graviditet/graviditetsbesvar-och-sjukdomar/graviditetsdiabetes--hoga-blodsockervarden-under-graviditet/',
            'topic': 'Gestational diabetes'
        },
        {
            'regional': 'https://www.1177.se/Vastmanland/barn--gravid/graviditet/undersokningar-under-graviditeten/besok-hos-barnmorskan-under-graviditeten/',
            'national_guess': 'https://www.1177.se/barn--gravid/graviditet/undersokningar-under-graviditeten/besok-hos-barnmorskan/',
            'topic': 'Midwife visits'
        }
    ]
    
    print("="*70)
    print("REGIONAL vs NATIONAL CONTENT COMPARISON")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['topic']}")
        print(f"{'='*70}")
        
        print(f"\n📍 Regional: {test['regional']}")
        regional_content = get_page_content(test['regional'])
        
        if not regional_content:
            print("  ❌ Could not fetch regional content")
            continue
        
        print(f"  ✅ Title: {regional_content['title']}")
        print(f"  📄 Length: {regional_content['length']} characters")
        
        time.sleep(2)
        
        print(f"\n🌍 National: {test['national_guess']}")
        national_content = get_page_content(test['national_guess'])
        
        if not national_content:
            print("  ⚠️  Could not fetch national equivalent (might not exist)")
            print(f"\n💡 CONCLUSION: Regional page may have UNIQUE content!")
            continue
        
        print(f"  ✅ Title: {national_content['title']}")
        print(f"  📄 Length: {national_content['length']} characters")
        
        # Compare
        similarity = similarity_ratio(
            regional_content['body'], 
            national_content['body']
        )
        
        print(f"\n📊 SIMILARITY: {similarity*100:.1f}%")
        
        if similarity > 0.90:
            print(f"  ✅ DUPLICATE - Very similar content ({similarity*100:.1f}%)")
            print(f"  → Can safely skip regional version")
        elif similarity > 0.70:
            print(f"  ⚠️  SIMILAR - Mostly same content with regional variations ({similarity*100:.1f}%)")
            print(f"  → Regional version has some unique info")
        else:
            print(f"  ❌ DIFFERENT - Unique regional content ({similarity*100:.1f}%)")
            print(f"  → Should keep BOTH versions")
        
        # Show sample differences if similar but not identical
        if 0.70 < similarity < 0.95:
            print(f"\n  🔍 Sample regional-specific content:")
            regional_unique = find_unique_phrases(
                regional_content['body'], 
                national_content['body']
            )
            for phrase in regional_unique[:3]:
                print(f"     • {phrase[:100]}...")
        
        time.sleep(2)  # Be polite to server


def find_unique_phrases(text1, text2, min_length=50):
    """Find phrases in text1 that don't appear in text2"""
    # Simple implementation - split into sentences
    sentences1 = [s.strip() for s in text1.split('.') if len(s.strip()) > min_length]
    sentences2_set = set([s.strip().lower() for s in text2.split('.')])
    
    unique = []
    for sentence in sentences1[:10]:  # Check first 10 sentences
        if sentence.lower() not in sentences2_set:
            unique.append(sentence)
    
    return unique


def analyze_url_patterns():
    """Analyze what types of content are regional"""
    
    from tier2_top200 import URLS
    
    regional_topics = {}
    national_count = 0
    regional_count = 0
    
    regions = [
        'Blekinge', 'Dalarna', 'Gotland', 'Gavleborg',
        'Halland', 'Jamtland', 'Jonkopings-lan', 'Kalmar',
        'Kronoberg', 'Norrbotten', 'Orebro', 'Ostergotland',
        'Skane', 'Sodermanland', 'Stockholm', 'Uppsala',
        'Varmland', 'Vasterbotten', 'Vasternorrland', 'Vastmanland',
        'Vastra-Gotaland'
    ]
    
    print("\n" + "="*70)
    print("URL PATTERN ANALYSIS")
    print("="*70)
    
    for url in URLS:
        is_regional = any(f'/{region}/' in url for region in regions)
        
        if is_regional:
            regional_count += 1
            # Extract topic
            parts = url.split('/')
            if len(parts) > 5:
                topic = parts[-2] if parts[-1] == '' else parts[-1]
                regional_topics[topic] = regional_topics.get(topic, 0) + 1
        else:
            national_count += 1
    
    print(f"\n📊 Statistics:")
    print(f"   National URLs: {national_count}")
    print(f"   Regional URLs: {regional_count}")
    print(f"   Ratio: {regional_count/len(URLS)*100:.1f}% are regional")
    
    print(f"\n📂 Top regional topics:")
    for topic, count in sorted(regional_topics.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {topic:50s}: {count}")
    
    return national_count, regional_count


if __name__ == "__main__":
    # First analyze patterns
    analyze_url_patterns()
    
    # Then compare actual content
    print("\n" + "="*70)
    print("Starting content comparison...")
    print("="*70)
    
    compare_regional_vs_national()
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
