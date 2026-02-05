import sys
import io
import asyncio
import logging
import re
import random
import json
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from curl_cffi.requests import AsyncSession
from playwright.async_api import Page, BrowserContext

# [3OX] Unicode Resilience Shield
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

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

    # Phase 41: Market Intelligence
    first_seen_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    is_sold: bool = False
    original_listing_date: Optional[datetime] = None
    last_price_update: Optional[datetime] = None
    
    # Phase 42: Price Intelligence (Research-backed)
    shipping_price: Optional[float] = 0.0
    total_price: Optional[float] = None

class BaseScraper(ABC):
    """
    Base Class for all Oracle Scrapers.
    Provides robust navigation, anti-detection, and metrics.
    """
    def __init__(self, shop_name: str, base_url: str = ""):
        self.spider_name = shop_name # Architecture Phase 41 Standard
        self.shop_name = shop_name # For repository compatibility
        self.base_url = base_url
        self.items_scraped = 0
        self.errors = 0
        self.blocked = False
        self.audit_logger = None # Optional AuditLogger injection
        self.log_callback = None # Function(str) to bridge logs to UI
        self.max_pages = 100  # Default max pages to crawl
        self.is_auction_source = False # True for Wallapop/eBay

    @abstractmethod
    async def search(self, query: str) -> List[ScrapedOffer]:
        """Entry point for searching items by query or 'auto' for global scan."""
        pass
    
    def _log(self, message: str, level: str = "info"):
        """Internal logger that also triggers the UI callback if registered."""
        # 1. Standard Python Logging
        lvl = getattr(logging, level.upper(), logging.INFO)
        logger.log(lvl, f"[{self.spider_name}] {message}")
        
        # 2. UI Tactical Console Bridge
        if self.log_callback:
            try:
                self.log_callback(message)
            except:
                pass

    def _get_random_header(self) -> dict:
        """Returns a consistent randomized header suite."""
        # Use a fixed consistent set to avoid mismatch detection
        versions = [
            ("131.0.0.0", "131"),
            ("130.0.0.0", "130"),
            ("129.0.0.0", "129")
        ]
        ver_full, ver_major = random.choice(versions)
        
        ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver_full} Safari/537.36"
        
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "sec-ch-ua": f'"Not_A Brand";v="8", "Chromium";v="{ver_major}", "Google Chrome";v="{ver_major}"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
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
                self._log(f"🧭 Navegando a {url} (Intento {attempt+1}, Modo: {strategy})...")
                await page.goto(url, wait_until=strategy, timeout=timeout)
                return True
            except Exception as e:
                self._log(f"⚠️ Reintento {attempt+1} fallido: {str(e)[:50]}...", level="warning")
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
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def _curl_get(self, url: str, impersonate: str = "chrome120") -> Optional[str]:
        """
        Stealth GET request using curl-cffi impersonation.
        Bypasses most TLS-based bot detection.
        """
        try:
            headers = self._get_random_header()
            async with AsyncSession() as session:
                self._log(f"🌩️ Infiltración vía curl-cffi (impersonate={impersonate}) a {url}...")
                resp = await session.get(url, headers=headers, impersonate=impersonate, timeout=30)
                
                if resp.status_code == 200:
                    return resp.text
                
                if resp.status_code in [403, 429]:
                    self._log(f"⚠️ Bloqueo detectado (HTTP {resp.status_code})...", level="warning")
                    self._detect_block(resp.text)
                    self.blocked = True
                else:
                    self._log(f"❌ Error HTTP {resp.status_code} en {url}", level="error")
                
                return None
        except Exception as e:
            self._log(f"❌ Fallo crítico en curl-get: {str(e)[:100]}", level="error")
            return None

    def _detect_block(self, html_content: str):
        """Analyzes HTML for common block patterns and logs snippets."""
        patterns = {
            "CAPTCHA": r"captcha|robot|human|verify",
            "Cloudflare": r"cloudflare|ray id|checking your browser",
            "DataDome": r"datadome|dd=",
            "Amazon Block": r"api-services-support|access denied"
        }
        
        for name, pattern in patterns.items():
            if re.search(pattern, html_content, re.IGNORECASE):
                self._log(f"🛡️ Bloqueo detectado: {name}", level="warning")
                # Log snippet for diagnosis
                snippet = html_content[:200].replace('\n', ' ')
                self._log(f"🔍 Snippet: {snippet}...", level="debug")
                return True
        return False


# end of file
