"""
Smart Web Scraper — Core Engine
AI-powered extraction with BeautifulSoup
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .anti_bot import AntiBotBypass
from .ai_selector import AISelector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartScraper:
    """
    AI-powered web scraper that adapts to layout changes automatically.
    Handles anti-bot protection, dynamic content, and complex pagination.
    """

    def __init__(self, url: str, use_ai: bool = True, delay: float = 1.5):
        self.url = url
        self.use_ai = use_ai
        self.delay = delay
        self.session = requests.Session()
        self.anti_bot = AntiBotBypass()
        self.ai_selector = AISelector() if use_ai else None
        self.data: List[Dict] = []

        # Apply anti-bot headers
        self.session.headers.update(self.anti_bot.get_headers())

    def fetch(self, url: Optional[str] = None) -> BeautifulSoup:
        """Fetch page with anti-bot bypass."""
        target = url or self.url
        try:
            time.sleep(self.delay)
            response = self.session.get(
                target,
                proxies=self.anti_bot.get_proxy(),
                timeout=30
            )
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            logger.error(f"Fetch error: {e}")
            return None

    def extract(self, fields: List[str], url: Optional[str] = None) -> List[Dict]:
        """
        AI-powered field extraction.
        Automatically detects CSS selectors for requested fields.
        """
        soup = self.fetch(url)
        if not soup:
            return []

        results = []

        if self.use_ai and self.ai_selector:
            # AI detects selectors automatically
            selectors = self.ai_selector.detect_selectors(soup, fields)
        else:
            # Fallback: common patterns
            selectors = self._default_selectors(fields)

        # Find all items (cards, rows, listings)
        containers = self._find_containers(soup)

        for container in containers:
            item = {}
            for field, selector in selectors.items():
                element = container.select_one(selector)
                if element:
                    item[field] = element.get_text(strip=True)
                else:
                    item[field] = None
            if any(item.values()):
                results.append(item)

        self.data = results
        logger.info(f"Extracted {len(results)} items from {url or self.url}")
        return results

    def extract_all_pages(self, fields: List[str], max_pages: int = 10) -> List[Dict]:
        """Scrape multiple pages automatically."""
        all_data = []
        soup = self.fetch()
        page = 1

        while soup and page <= max_pages:
            logger.info(f"Scraping page {page}...")
            page_data = self.extract(fields)
            all_data.extend(page_data)

            # Find next page
            next_url = self._find_next_page(soup)
            if not next_url:
                break

            soup = self.fetch(next_url)
            page += 1

        self.data = all_data
        return all_data

    def _find_containers(self, soup: BeautifulSoup) -> List:
        """Find repeating elements (product cards, articles, etc.)."""
        common_selectors = [
            ".product", ".item", ".card", ".listing",
            "article", ".result", ".post", "[data-item]",
            ".product-item", ".search-result"
        ]
        for selector in common_selectors:
            items = soup.select(selector)
            if len(items) > 2:
                return items

        # Fallback: find repeating divs
        return soup.select("div[class]")[:50]

    def _find_next_page(self, soup: BeautifulSoup) -> Optional[str]:
        """Detect next page URL from pagination."""
        selectors = [
            "a[rel='next']", ".next a", ".pagination .next",
            "a:contains('Next')", "a:contains('→')", ".page-next a"
        ]
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.get("href"):
                    href = element["href"]
                    if href.startswith("http"):
                        return href
                    from urllib.parse import urljoin
                    return urljoin(self.url, href)
            except Exception:
                continue
        return None

    def _default_selectors(self, fields: List[str]) -> Dict[str, str]:
        """Common CSS selectors for typical fields."""
        defaults = {
            "title":       "h1, h2, h3, .title, .name, .product-name",
            "price":       ".price, .cost, [class*='price'], [itemprop='price']",
            "description": ".description, .desc, p, .summary",
            "image":       "img",
            "link":        "a",
            "rating":      ".rating, .stars, [class*='rating']",
            "category":    ".category, .tag, .breadcrumb",
            "date":        "time, .date, .published, [datetime]",
            "author":      ".author, .by, [rel='author']",
        }
        return {f: defaults.get(f, f".{f}") for f in fields}

    def save_to_db(self, data: Optional[List[Dict]] = None, table: str = "scraped_data"):
        """Save results to SQLite database."""
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        db.insert_many(table, data or self.data)
        logger.info(f"Saved {len(data or self.data)} records to '{table}'")

    def export_csv(self, path: str):
        """Export results to CSV."""
        from exporters.export import Exporter
        Exporter(self.data).to_csv(path)

    def export_json(self, path: str):
        """Export results to JSON."""
        from exporters.export import Exporter
        Exporter(self.data).to_json(path)

    def export_excel(self, path: str):
        """Export results to Excel."""
        from exporters.export import Exporter
        Exporter(self.data).to_excel(path)

    def __repr__(self):
        return f"SmartScraper(url={self.url}, items={len(self.data)})"
