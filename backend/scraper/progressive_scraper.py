import requests
import time
import sys
from pathlib import Path
from improved_scraper import ImprovedHealthScraper
import json
from datetime import datetime

def progressive_scrape(tier='tier1_top100'):
    """
    Scrape progressively:
    - Tier 1: Top 100 (most important)
    - Tier 2: Top 200 (comprehensive)
    - Tier 3: Top 500 (complete coverage)
    """
    
    # Import the appropriate tier
    if tier == 'tier1_top100':
        from tier1_top100 import URLS
    elif tier == 'tier2_top200':
        from tier2_top200 import URLS
    elif tier == 'tier3_comprehensive':
        from tier3_comprehensive import URLS
    else:
        from all_urls import URLS
    
    scraper = ImprovedHealthScraper()
    results = []
    failed_urls = []
    
    print("="*70)
    print(f"PROGRESSIVE SCRAPER - {tier.upper()}")
    print(f"Target: {len(URLS)} URLs")
    print("="*70)
    print(f"⏱️  Estimated time: {len(URLS) * 2.5 / 60:.1f} minutes")
    print("="*70)
    
    start_time = time.time()
    checkpoint_interval = 25
    
    for i, url in enumerate(URLS, 1):
        # Progress indicator
        progress = f"[{i}/{len(URLS)}] ({i/len(URLS)*100:.1f}%)"
        print(f"\n{progress} {url.split('/')[-2] if '/' in url else url}")
        
        try:
            result = scraper.scrape_page(url)
            
            if result and result.get('content_length', 0) > 200:
                print(f"  ✅ {result['title'][:60]}")
                print(f"     {result['content_length']:,} chars | {result['num_sections']} sections")
                results.append(result)
            else:
                print(f"  ⚠️  Skipped - insufficient content")
                failed_urls.append({'url': url, 'reason': 'insufficient_content'})
                
        except requests.exceptions.Timeout:
            print(f"  ⏱️  Timeout")
            failed_urls.append({'url': url, 'reason': 'timeout'})
            
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"  ❌ {error_msg}")
            failed_urls.append({'url': url, 'reason': error_msg})
        
        # Checkpoint save
        if i % checkpoint_interval == 0:
            checkpoint_file = f'checkpoint_{tier}_{i}.json'
            scraper.save_to_json(results, filename=checkpoint_file)
            print(f"\n💾 Checkpoint: {len(results)} pages saved to {checkpoint_file}")
            
            # Stats so far
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (len(URLS) - i) / rate
            print(f"   ⏱️  {elapsed/60:.1f} min elapsed, ~{remaining/60:.1f} min remaining")
            print(f"   📊 Success rate: {len(results)/i*100:.1f}%")
        
        # Respectful delay
        time.sleep(2.5)  # Slightly longer delay for large scrape
    
    # Final save
    elapsed = time.time() - start_time
    output_file = f'{tier}_scraped_{datetime.now().strftime("%Y%m%d")}.json'
    
    print("\n" + "="*70)
    if results:
        scraper.save_to_json(results, filename=output_file)
        
        # Statistics
        total_chars = sum(r['content_length'] for r in results)
        total_sections = sum(r['num_sections'] for r in results)
        avg_chars = total_chars / len(results)
        
        print(f"✅ SUCCESS!")
        print(f"   Pages scraped: {len(results)}/{len(URLS)} ({len(results)/len(URLS)*100:.1f}%)")
        print(f"   Time taken: {elapsed/60:.1f} minutes")
        print(f"   Rate: {len(results)/(elapsed/60):.1f} pages/minute")
        print(f"   Total content: {total_chars:,} characters")
        print(f"   Total sections: {total_sections:,}")
        print(f"   Average per page: {avg_chars:,.0f} characters")
        print(f"   Saved to: data/{output_file}")
        
    else:
        print("❌ No pages scraped successfully")
    
    # Failed URLs report
    if failed_urls:
        fail_file = f'failed_{tier}.json'
        with open(f'data/{fail_file}', 'w') as f:
            json.dump(failed_urls, f, indent=2)
        
        print(f"\n⚠️  Failed URLs: {len(failed_urls)}")
        print(f"   Saved to: data/{fail_file}")
        
        # Breakdown by reason
        reasons = {}
        for fail in failed_urls:
            reason = fail['reason']
            reasons[reason] = reasons.get(reason, 0) + 1
        
        print(f"\n   Failure reasons:")
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"     {reason[:50]:50s}: {count}")
    
    print("="*70)
    
    return len(results), len(failed_urls)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Progressive scraper for 1177.se')
    parser.add_argument('--tier', 
                       choices=['tier1_top100', 'tier2_top200', 'tier3_comprehensive', 'all'],
                       default='tier2_top200',
                       help='Which tier to scrape')
    
    args = parser.parse_args()
    
    try:
        success, failed = progressive_scrape(args.tier)
        sys.exit(0 if success > len(URLS) * 0.8 else 1)  # Need 80% success
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted! Check checkpoint files for progress.")
        sys.exit(1)
