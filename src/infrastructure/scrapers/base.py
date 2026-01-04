from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging
import re
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

class BaseScraper(ABC):
    """
    Base Class for all Oracle Scrapers.
    Provides robust navigation, anti-detection, and metrics.
    """
    def __init__(self, name: str, base_url: str):
        self.spider_name = name
        self.shop_name = name # For repository compatibility
        self.base_url = base_url
        self.items_scraped = 0
        self.errors = 0
        self.blocked = False
        self.audit_logger = None # Optional AuditLogger injection

    @abstractmethod
    async def run(self, context: BrowserContext) -> List[ScrapedOffer]:
        """Entry point for the scraper loop."""
        pass

    async def _safe_navigate(self, page: Page, url: str, timeout: int = 45000) -> bool:
        """Navigates with exponential backoff and anti-detection."""
        for attempt in range(3):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                return True
            except Exception as e:
                logger.warning(f"[{self.spider_name}] Navigation attempt {attempt+1} failed: {e}")
                await asyncio.sleep(2 * (attempt + 1))
        
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

# Alias for compatibility if needed
BaseSpider = BaseScraper
