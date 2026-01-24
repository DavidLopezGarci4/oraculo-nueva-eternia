from typing import List, Optional
import asyncio
import logging
import random
from playwright.async_api import BrowserContext, Page
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class Time4ActionToysDEScraper(BaseScraper):
    """
    Scraper for Time4ActionToys.de (Germany - Specialized Action Figures Shop).
    Phase 8.4b: Advanced Expansion.
    Pagination: ?p=1, ?p=2, etc.
    Uses Shopware-style product structure.
    """
    def __init__(self):
        super().__init__(
            shop_name="Time4ActionToysDE",
            base_url="https://time4actiontoys.de/masters-of-the-universe"
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        from playwright.async_api import async_playwright
        
        products: List[ScrapedOffer] = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._get_random_header()["User-Agent"]
            )
            page = await context.new_page()
            
            try:
                page_num = 1
                max_pages = 10
                
                while page_num <= max_pages:
                    # Time4ActionToys uses ?p=1 format for pagination
                    current_url = f"{self.base_url}?p={page_num}"
                    
                    logger.info(f"[{self.scraper_name}] Scraping page {page_num}: {current_url}")
                    
                    if not await self._safe_navigate(page, current_url):
                        break
                    
                    await self._random_sleep(1.5, 3.0)
                    
                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Shopware-style product structure
                    items = soup.select('.product-box, .product--box, .product-card, article.product')
                    
                    if not items:
                        items = soup.select('[class*="product"], .cms-listing-col')
                    
                    logger.info(f"[{self.scraper_name}] Found {len(items)} items on page {page_num}")
                    
                    if not items:
                        break
                    
                    for item in items:
                        prod = self._parse_item(item)
                        if prod:
                            products.append(prod)
                            self.items_scraped += 1
                    
                    page_num += 1
                        
            except Exception as e:
                logger.error(f"[{self.scraper_name}] Critical Error: {e}", exc_info=True)
                self.errors += 1
            finally:
                await browser.close()
                
        logger.info(f"[{self.scraper_name}] Finished. Total items: {len(products)}")
        return products

    def _parse_item(self, item) -> Optional[ScrapedOffer]:
        try:
            a_tag = item.select_one('a[href]')
            if not a_tag:
                return None
            
            link = a_tag.get('href')
            if not link.startswith('http'):
                link = f"https://time4actiontoys.de{link}"
            
            # Title: Shopware uses .product-name or .product--title
            title_tag = item.select_one('.product-name, .product--title, .product-title, h2, h3')
            name = title_tag.get_text(strip=True) if title_tag else a_tag.get('title', '')
            
            if not name or len(name) < 5:
                return None
            
            # Price: German format 12,95 €
            # Phase 11.2: Avoid concatenating list price with real price
            price_tag = item.select_one('.product-price, .product--price, .price')
            price_val = 0.0
            if price_tag:
                # If there's a discounted price, we must remove the 'list-price' part
                # to avoid strings like "14,9928,99"
                list_price_tag = price_tag.select_one('.list-price')
                if list_price_tag:
                    list_price_tag.decompose()
                
                price_val = self._normalize_price(price_tag.get_text(strip=True))
            
            if price_val == 0.0:
                return None
            
            # Availability
            is_avl = True
            if item.select_one('.is--not-available, .out-of-stock, .sold-out'):
                is_avl = False
            
            return ScrapedOffer(
                product_name=name,
                price=price_val,
                currency="EUR",
                url=link,
                shop_name=self.scraper_name,
                is_available=is_avl
            )
        except Exception as e:
            logger.warning(f"[{self.scraper_name}] Item parsing error: {e}")
            return None
