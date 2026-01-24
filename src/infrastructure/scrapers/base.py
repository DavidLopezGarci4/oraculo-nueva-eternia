from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging
import re
import random
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger(__name__)

class ScrapedOffer(BaseModel):
    product_name: str
    price: float
    currency: str = "EUR"
    url: str
    shop_name: str
    is_available: bool = True
    image_url: Optional[str] = None
    ean: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    source_type: str = "Retail" # Retail, Peer-to-Peer
    
    # Phase 39: Auction Intelligence
    sale_type: str = "Retail" # Retail, Auction, Fixed_P2P
    expiry_at: Optional[datetime] = None
    bids_count: int = 0
    time_left_raw: Optional[str] = None

class BaseScraper(ABC):
    """
    Base Class for all Oracle Scrapers.
    Provides robust navigation, anti-detection, and metrics.
    """
    def __init__(self, shop_name: str, base_url: str = ""):
        self.scraper_name = shop_name # Renamed from spider_name
        self.shop_name = shop_name # For repository compatibility
        self.base_url = base_url
        self.items_scraped = 0
        self.errors = 0
        self.blocked = False
        self.audit_logger = None # Optional AuditLogger injection
        self.max_pages = 100  # Default max pages to crawl
        self.is_auction_source = False # True for Wallapop/eBay

    @abstractmethod
    async def search(self, query: str) -> List[ScrapedOffer]:
        """Entry point for searching items by query or 'auto' for global scan."""
        pass

    def _get_random_header(self) -> dict:
        """Returns a randomized User-Agent header and modern fingerprints."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

    async def run(self, *args, **kwargs):
        """Legacy compatibility wrapper."""
        raise NotImplementedError("Oracle Scrapers now use .search(query)")

    async def _safe_navigate(self, page: Page, url: str, timeout: int = 60000) -> bool:
        """Navigates with exponential backoff and randomized wait strategies."""
        wait_strategies = ["domcontentloaded", "load", "networkidle"]
        
        for attempt in range(3):
            try:
                # Alternate wait strategies to bypass simple detection/loading issues
                strategy = random.choice(wait_strategies) if attempt > 0 else "domcontentloaded"
                await page.goto(url, wait_until=strategy, timeout=timeout)
                return True
            except Exception as e:
                logger.warning(f"[{self.scraper_name}] Navigation attempt {attempt+1} failed ({url}): {e}")
                # Exponential backoff: 3s, 6s, 12s...
                await asyncio.sleep(3 * (2 ** attempt))
        
        self.blocked = True
        return False

    def _normalize_price(self, raw_price_text: str) -> float:
        """Cleans messy price strings like '25,32 €' or 'Desde 12.00$'."""
        if not raw_price_text: return 0.0
        try:
            # Remove currency symbols and spaces
            txt = re.sub(r'[^0-9,.]', '', raw_price_text)
            # Handle European comma as decimal
            if ',' in txt and '.' in txt:
                txt = txt.replace(',', '') # 1,234.56 -> 1234.56
            elif ',' in txt:
                txt = txt.replace(',', '.') # 12,34 -> 12.34
            
            # Final cleanup
            return float(txt)
        except Exception:
            return 0.0

    async def _random_sleep(self, min_sec: float = 0.5, max_sec: float = 2.0):
        import random
        await asyncio.sleep(random.uniform(min_sec, max_sec))


# end of file
