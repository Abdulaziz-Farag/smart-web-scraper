"""
Example: Scrape e-commerce products
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.core import SmartScraper

# Scrape products from any e-commerce site
scraper = SmartScraper(
    url="https://books.toscrape.com",
    use_ai=True,
    delay=1.5
)

data = scraper.extract_all_pages(
    fields=["title", "price", "rating", "link"],
    max_pages=5
)

print(f"Found {len(data)} products\n")
for item in data[:5]:
    print(item)

# Export
scraper.export_csv("products.csv")
scraper.export_excel("products.xlsx")
scraper.save_to_db(table="products")
print("\nExported to CSV, Excel, and Database!")
