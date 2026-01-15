from typing import List, Optional
import asyncio
import logging
from playwright.async_api import BrowserContext, Page
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class DeToyboysNLScraper(BaseScraper):
    """
    Scraper for De Toyboys (Netherlands) - European MOTU Collector Shop.
    Phase 8.4: Expansión Continental.
    """
    def __init__(self):
        super().__init__(
            shop_name="DeToyboys",
            base_url="https://detoyboys.nl/en/collectibles/subline-masters-of-the-universe-origins"
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        """
        Executes the scraping logic for De Toyboys.
        """
        from playwright.async_api import async_playwright
        
        products: List[ScrapedOffer] = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._get_random_header()["User-Agent"]
            )
            page = await context.new_page()
            
            try:
                current_url = self.base_url
                page_num = 1
                max_pages = 50
                
                while current_url and page_num <= max_pages:
                    logger.info(f"[{self.spider_name}] Scraping page {page_num}: {current_url}")
                    
                    if not await self._safe_navigate(page, current_url):
                        break
                    
                    await self._random_sleep(1.5, 3.0)
                    
                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # De Toyboys uses standard WooCommerce/Shopify patterns
                    items = soup.select('.product-card, .product-item, .woocommerce-LoopProduct-link')
                    
                    if not items:
                        # Fallback: generic product listing
                        items = soup.select('[data-product-id], .product')
                    
                    logger.info(f"[{self.spider_name}] Found {len(items)} items on page {page_num}")
                    
                    for item in items:
                        prod = self._parse_item(item)
                        if prod:
                            products.append(prod)
                            self.items_scraped += 1
                    
                    # Pagination
                    next_btn = soup.select_one('a.next, [rel="next"], .pagination__next')
                    if next_btn and next_btn.get('href'):
                        next_href = next_btn.get('href')
                        current_url = next_href if next_href.startswith('http') else f"https://detoyboys.nl{next_href}"
                        page_num += 1
                    else:
                        break
                        
            except Exception as e:
                logger.error(f"[{self.spider_name}] Critical Error: {e}", exc_info=True)
                self.errors += 1
            finally:
                await browser.close()
                
        logger.info(f"[{self.spider_name}] Finished. Total items: {len(products)}")
        return products

    def _parse_item(self, item) -> Optional[ScrapedOffer]:
        try:
            # Find link
            a_tag = item.select_one('a[href]') or item
            link = a_tag.get('href') if hasattr(a_tag, 'get') else None
            
            if not link:
                return None
            
            if not link.startswith('http'):
                link = f"https://detoyboys.nl{link}"
            
            # Find name
            title_tag = item.select_one('.product-title, .product-name, h2, h3, .title')
            name = title_tag.get_text(strip=True) if title_tag else "Unknown"
            
            # Find price
            price_tag = item.select_one('.price, .product-price, [data-price]')
            price_val = 0.0
            if price_tag:
                price_val = self._normalize_price(price_tag.get_text(strip=True))
            
            if price_val == 0.0:
                return None
            
            # Availability
            is_avl = True
            if item.select_one('.out-of-stock, .sold-out, .unavailable'):
                is_avl = False
            
            return ScrapedOffer(
                product_name=name,
                price=price_val,
                currency="EUR",
                url=link,
                shop_name=self.spider_name,
                is_available=is_avl
            )
        except Exception as e:
            logger.warning(f"[{self.spider_name}] Item parsing error: {e}")
            return None
