"""
AI-Powered CSS Selector Detection
Automatically finds the right selectors for any website layout
"""

import re
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Optional
from collections import Counter


class AISelector:
    """
    Detects CSS selectors automatically using heuristics + AI patterns.
    Adapts when website layouts change — no manual updates needed.
    """

    FIELD_KEYWORDS = {
        "title":       ["title", "name", "heading", "product-name", "item-name"],
        "price":       ["price", "cost", "amount", "value", "sale"],
        "description": ["description", "desc", "summary", "detail", "about", "content"],
        "image":       ["image", "img", "photo", "picture", "thumbnail"],
        "link":        ["link", "url", "href"],
        "rating":      ["rating", "stars", "score", "review"],
        "category":    ["category", "cat", "tag", "label", "breadcrumb", "genre"],
        "date":        ["date", "time", "published", "created", "posted", "updated"],
        "author":      ["author", "writer", "by", "creator", "journalist"],
        "brand":       ["brand", "manufacturer", "vendor", "maker", "company"],
        "sku":         ["sku", "id", "code", "ref", "model", "barcode"],
        "stock":       ["stock", "availability", "qty", "quantity", "inventory"],
    }

    def detect_selectors(self, soup: BeautifulSoup, fields: List[str]) -> Dict[str, str]:
        """Main method: detect best selector for each field."""
        selectors = {}
        for field in fields:
            selector = self._find_best_selector(soup, field)
            selectors[field] = selector
        return selectors

    def _find_best_selector(self, soup: BeautifulSoup, field: str) -> str:
        """Find the best CSS selector for a field."""
        keywords = self.FIELD_KEYWORDS.get(field.lower(), [field])
        candidates = []

        # Strategy 1: class/id matching
        for tag in soup.find_all(True):
            class_list = tag.get("class", [])
            tag_id = tag.get("id", "")
            tag_itemprop = tag.get("itemprop", "")

            # Check itemprop (semantic HTML)
            if any(kw in tag_itemprop.lower() for kw in keywords):
                selector = f"[itemprop='{tag_itemprop}']"
                candidates.append((selector, 10))

            # Check class names
            for cls in class_list:
                if any(kw in cls.lower() for kw in keywords):
                    candidates.append((f".{cls}", 8))

            # Check id
            if any(kw in tag_id.lower() for kw in keywords):
                candidates.append((f"#{tag_id}", 9))

            # Check data attributes
            for attr, val in tag.attrs.items():
                if attr.startswith("data-") and isinstance(val, str):
                    if any(kw in val.lower() for kw in keywords):
                        candidates.append((f"[{attr}='{val}']", 7))

        # Strategy 2: semantic HTML tags
        semantic_map = {
            "title":   ["h1", "h2", "h3"],
            "date":    ["time"],
            "author":  ["address"],
            "image":   ["img"],
            "link":    ["a"],
            "price":   ["strong", "span"],
        }
        if field in semantic_map:
            for tag in semantic_map[field]:
                candidates.append((tag, 5))

        # Return best candidate
        if candidates:
            best = max(candidates, key=lambda x: x[1])
            return best[0]

        return f".{field}"

    def analyze_page_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze page structure to understand layout."""
        analysis = {
            "has_pagination":   bool(soup.find(class_=re.compile(r"pag|next|prev", re.I))),
            "has_login":        bool(soup.find("input", {"type": "password"})),
            "has_search":       bool(soup.find("input", {"type": "search"})),
            "total_links":      len(soup.find_all("a")),
            "total_images":     len(soup.find_all("img")),
            "repeating_items":  self._count_repeating(soup),
            "has_json_ld":      bool(soup.find("script", {"type": "application/ld+json"})),
        }
        return analysis

    def _count_repeating(self, soup: BeautifulSoup) -> int:
        """Count repeating elements (like product cards)."""
        class_counter = Counter()
        for tag in soup.find_all(True):
            for cls in tag.get("class", []):
                class_counter[cls] += 1
        repeating = [cls for cls, count in class_counter.items() if count > 3]
        return len(repeating)

    def extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract structured data from JSON-LD."""
        import json
        script = soup.find("script", {"type": "application/ld+json"})
        if script:
            try:
                return json.loads(script.string)
            except Exception:
                return None
        return None
