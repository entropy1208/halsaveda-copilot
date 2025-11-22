# Scrape top 100 most viewed 1177 pages
urls = [
    # Add 100 URLs from 1177.se sitemap
]

# Run overnight
for url in urls:
    scrape_page(url)
    time.sleep(2)  # Be polite
