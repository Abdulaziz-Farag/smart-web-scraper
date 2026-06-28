"""
Example: Scrape news articles
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.core import SmartScraper

scraper = SmartScraper(
    url="https://news.ycombinator.com",
    use_ai=True,
    delay=1.0
)

data = scraper.extract_all_pages(
    fields=["title", "link", "author", "date", "category"],
    max_pages=3
)

print(f"Found {len(data)} articles\n")
for item in data[:5]:
    print(item)

scraper.export_json("articles.json")
scraper.export_csv("articles.csv")
print("\nSaved articles to JSON and CSV!")
