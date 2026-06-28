"""
Anti-Bot Bypass Module
Handles headers, proxies, delays, and fingerprint rotation
"""

import random
import time
from fake_useragent import UserAgent
from typing import Dict, Optional


class AntiBotBypass:
    """Bypass common anti-bot protections."""

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

        self.proxies_list = []  # Add your proxies here
        self._request_count = 0

    def get_headers(self) -> Dict[str, str]:
        """Generate realistic browser headers."""
        user_agent = self._get_user_agent()
        return {
            "User-Agent":      user_agent,
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection":      "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest":  "document",
            "Sec-Fetch-Mode":  "navigate",
            "Sec-Fetch-Site":  "none",
            "Cache-Control":   "max-age=0",
        }

    def get_proxy(self) -> Optional[Dict]:
        """Return a random proxy if available."""
        if not self.proxies_list:
            return None
        proxy = random.choice(self.proxies_list)
        return {"http": proxy, "https": proxy}

    def add_proxies(self, proxies: list):
        """Add proxy list."""
        self.proxies_list.extend(proxies)

    def smart_delay(self, min_sec: float = 1.0, max_sec: float = 3.5):
        """Human-like random delay between requests."""
        self._request_count += 1
        # Every 10 requests, take a longer break
        if self._request_count % 10 == 0:
            time.sleep(random.uniform(5, 10))
        else:
            time.sleep(random.uniform(min_sec, max_sec))

    def _get_user_agent(self) -> str:
        """Get random user agent."""
        fallback_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]
        try:
            return self.ua.random if self.ua else random.choice(fallback_agents)
        except Exception:
            return random.choice(fallback_agents)
