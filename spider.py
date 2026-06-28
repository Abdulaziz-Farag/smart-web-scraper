"""
Scrapy Spider — Large-scale async crawling
10x faster than requests for big jobs
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SmartSpider(scrapy.Spider):
    """Base smart spider with anti-bot and AI selection."""

    name = "smart_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY":           True,
        "DOWNLOAD_DELAY":           1.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS":      8,
        "RETRY_TIMES":              3,
        "HTTPCACHE_ENABLED":        True,
        "LOG_LEVEL":                "WARNING",
        "DEFAULT_REQUEST_HEADERS": {
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
        },
    }

    def __init__(self, start_url: str, fields: List[str],
                 max_pages: int = 50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.fields = fields
        self.max_pages = max_pages
        self.pages_crawled = 0
        self.results: List[Dict] = []

    def parse(self, response):
        """Parse each page."""
        self.pages_crawled += 1

        # Extract items
        items = self._extract_items(response)
        self.results.extend(items)
        yield from items

        # Follow next page
        if self.pages_crawled < self.max_pages:
            next_page = self._find_next(response)
            if next_page:
                yield response.follow(next_page, self.parse)

    def _extract_items(self, response) -> List[Dict]:
        """Extract data from response."""
        items = []
        containers = response.css(
            ".product, .item, .card, article, .listing, .result"
        )

        if not containers:
            # Single item page
            item = {field: self._extract_field(response, field)
                    for field in self.fields}
            if any(item.values()):
                items.append(item)
        else:
            for container in containers:
                item = {field: self._extract_field(container, field)
                        for field in self.fields}
                if any(item.values()):
                    items.append(item)

        return items

    def _extract_field(self, selector, field: str) -> Optional[str]:
        """Smart field extraction."""
        selectors_map = {
            "title":       ["h1::text", "h2::text", ".title::text", ".name::text", "[itemprop='name']::text"],
            "price":       [".price::text", "[itemprop='price']::attr(content)", ".cost::text", "strong::text"],
            "description": [".description::text", "[itemprop='description']::text", "p::text"],
            "image":       ["img::attr(src)", "[itemprop='image']::attr(src)"],
            "link":        ["a::attr(href)"],
            "rating":      [".rating::text", "[itemprop='ratingValue']::attr(content)"],
            "date":        ["time::attr(datetime)", ".date::text", "[itemprop='datePublished']::text"],
            "author":      [".author::text", "[itemprop='author']::text", "[rel='author']::text"],
            "category":    [".category::text", ".tag::text", ".breadcrumb li:last-child::text"],
            "brand":       ["[itemprop='brand']::text", ".brand::text"],
        }

        for css in selectors_map.get(field, [f".{field}::text"]):
            value = selector.css(css).get()
            if value:
                return value.strip()
        return None

    def _find_next(self, response) -> Optional[str]:
        """Find next page URL."""
        selectors = [
            "a[rel='next']::attr(href)",
            ".next a::attr(href)",
            ".pagination .active + li a::attr(href)",
            "a:contains('Next')::attr(href)",
        ]
        for sel in selectors:
            url = response.css(sel).get()
            if url:
                return url
        return None


class EcommerceSpider(SmartSpider):
    """Specialized spider for e-commerce sites."""
    name = "ecommerce_spider"

    def _extract_items(self, response):
        for product in response.css(".product, .product-item, [data-product]"):
            yield {
                "title":       product.css("h2::text, .product-name::text").get("").strip(),
                "price":       product.css(".price::text, .amount::text").get("").strip(),
                "image":       product.css("img::attr(src)").get(""),
                "link":        product.css("a::attr(href)").get(""),
                "rating":      product.css(".rating::text, .stars::text").get(""),
                "availability": product.css(".stock::text, .availability::text").get(""),
                "source_url":  response.url,
            }


class NewsSpider(SmartSpider):
    """Specialized spider for news & blog sites."""
    name = "news_spider"

    def _extract_items(self, response):
        for article in response.css("article, .post, .news-item, .article"):
            yield {
                "title":   article.css("h1::text, h2::text, .headline::text").get("").strip(),
                "summary": article.css("p::text, .excerpt::text").get("").strip(),
                "author":  article.css(".author::text, [rel='author']::text").get(""),
                "date":    article.css("time::attr(datetime), .date::text").get(""),
                "link":    article.css("a::attr(href)").get(""),
                "image":   article.css("img::attr(src)").get(""),
                "category": article.css(".category::text, .tag::text").get(""),
                "source_url": response.url,
            }


def run_spider(spider_class, start_url: str, fields: List[str],
               max_pages: int = 50) -> List[Dict]:
    """Run a spider and return collected data."""
    results = []

    class CollectorPipeline:
        def process_item(self, item, spider):
            results.append(dict(item))
            return item

    settings = get_project_settings()
    settings.set("ITEM_PIPELINES", {CollectorPipeline: 100})

    process = CrawlerProcess(settings)
    process.crawl(spider_class, start_url=start_url,
                  fields=fields, max_pages=max_pages)
    process.start()

    return results
