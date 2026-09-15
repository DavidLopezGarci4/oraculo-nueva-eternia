from typing import List, Optional
import asyncio
import logging
from playwright.async_api import BrowserContext, Page
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper
from src.infrastructure.scrapers.base import ScrapedOffer

# Configure Logger
logger = logging.getLogger(__name__)

class FantasiaScraper(BaseScraper):
    """
    Scraper for Fantasia Personajes (PrestaShop).
    Uses fast curl-cffi impersonation with automatic fallback to Playwright,
    focused MOTU Origins search query, and direct tracking of catalog items.
    """
    KNOWN_PRODUCT_URLS: List[str] = [
        "https://fantasiapersonajes.es/masters-of-the-universe-origins-man-at-arms-14-cm-mattel"
    ]

    def __init__(self):
        super().__init__(
            shop_name="Fantasia Personajes",
            base_url="https://fantasiapersonajes.es/busqueda?controller=search&s=masters+of+the+universe+origins&resultsPerPage=36"
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        import urllib.parse
        products: List[ScrapedOffer] = []
        seen_urls = set()

        # 1. Resolve search URL
        if query and query not in ("auto", "*"):
            encoded = urllib.parse.quote_plus(query)
            search_url = f"https://fantasiapersonajes.es/busqueda?controller=search&s={encoded}&resultsPerPage=36"
        else:
            search_url = self.base_url

        # 2. Try fast stealth crawl via curl-cffi
        try:
            current_url = search_url
            page_num = 1
            max_pages = 10

            while current_url and page_num <= max_pages:
                logger.info(f"[{self.spider_name}] Fast-crawling page {page_num}: {current_url}")
                html = await self._curl_get(current_url)
                if not html:
                    break

                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('article.product-miniature, .product-miniature')
                if not items:
                    # Check JSON-LD fallback
                    json_prods = self._extract_from_json_ld(soup)
                    for jp in json_prods:
                        if jp.url not in seen_urls:
                            seen_urls.add(jp.url)
                            products.append(jp)
                            self.items_scraped += 1
                else:
                    for item in items:
                        prod = self._parse_html_item(item)
                        if prod and prod.url not in seen_urls:
                            seen_urls.add(prod.url)
                            products.append(prod)
                            self.items_scraped += 1

                # Pagination
                next_tag = soup.select_one('a.next.js-search-link, li.next a')
                if next_tag and next_tag.get('href') and 'javascript:void' not in next_tag.get('href'):
                    next_url = next_tag.get('href')
                    if next_url.startswith('/'):
                        next_url = f"https://fantasiapersonajes.es{next_url}"
                    current_url = next_url
                    page_num += 1
                    await asyncio.sleep(0.5)
                else:
                    break

            # 3. Process known catalog items that might be hidden from search
            for direct_url in self.KNOWN_PRODUCT_URLS:
                if direct_url not in seen_urls:
                    p_html = await self._curl_get(direct_url)
                    if p_html:
                        p_soup = BeautifulSoup(p_html, 'html.parser')
                        p_prod = self._parse_product_page(p_soup, direct_url)
                        if p_prod and p_prod.url not in seen_urls:
                            seen_urls.add(p_prod.url)
                            products.append(p_prod)
                            self.items_scraped += 1

            if products:
                logger.info(f"[{self.spider_name}] Fast crawl finished. Total items: {len(products)}")
                return products

        except Exception as e:
            logger.warning(f"[{self.spider_name}] Fast crawl encountered error: {e}. Falling back to Playwright.")

        # Fallback to Playwright if curl-cffi yielded no results or was blocked
        return await self._search_playwright(search_url)

    async def _search_playwright(self, search_url: str) -> List[ScrapedOffer]:
        from playwright.async_api import async_playwright
        products: List[ScrapedOffer] = []
        seen_urls = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self._get_random_header()["User-Agent"])
            page = await context.new_page()

            try:
                current_url = search_url
                page_num = 1
                max_pages = 10

                while current_url and page_num <= max_pages:
                    logger.info(f"[{self.spider_name}] [Playwright] Scraping page {page_num}: {current_url}")

                    if not await self._safe_navigate(page, current_url):
                        break

                    await self._handle_popups(page)
                    await asyncio.sleep(1.0)

                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')

                    items = soup.select('article.product-miniature, .product-miniature')
                    for item in items:
                        prod = self._parse_html_item(item)
                        if prod and prod.url not in seen_urls:
                            seen_urls.add(prod.url)
                            products.append(prod)
                            self.items_scraped += 1

                    next_tag = soup.select_one('a.next.js-search-link, li.next a')
                    if next_tag and next_tag.get('href') and 'javascript:void' not in next_tag.get('href'):
                        next_url = next_tag.get('href')
                        if next_url.startswith('/'):
                            next_url = f"https://fantasiapersonajes.es{next_url}"
                        current_url = next_url
                        page_num += 1
                    else:
                        break

            except Exception as e:
                logger.error(f"[{self.spider_name}] Playwright Critical Error: {e}", exc_info=True)
                self.errors += 1
            finally:
                await browser.close()

        logger.info(f"[{self.spider_name}] Playwright Finished. Total items: {len(products)}")
        return products

    def _parse_product_page(self, soup: BeautifulSoup, url: str) -> Optional[ScrapedOffer]:
        try:
            h1 = soup.select_one('h1[itemprop="name"], h1.h1, h1')
            if not h1:
                return None
            name = h1.get_text(strip=True)

            price_val = 0.0
            price_el = soup.select_one('span[itemprop="price"], .current-price span[itemprop="price"], .current-price span, .product-prices span')
            if price_el:
                if price_el.has_attr('content'):
                    try:
                        price_val = float(price_el['content'].replace(',', '.'))
                    except:
                        pass
                if price_val == 0.0:
                    price_val = self._normalize_price(price_el.get_text(strip=True))

            if price_val == 0.0:
                return None

            is_avl = True
            if soup.select_one('.product-flags .out-of-stock, .product-unavailable'):
                is_avl = False

            item_text = soup.get_text(strip=True).lower()
            if any(term in item_text for term in ["agotado", "no disponible", "sin existencias"]):
                if soup.select_one('.product-unavailable, .out-of-stock'):
                    is_avl = False

            img = soup.select_one('.product-cover img, img[itemprop="image"]')
            img_url = None
            if img:
                img_url = img.get('data-src') or img.get('src')
                if img_url and img_url.startswith('/'):
                    img_url = f"https://fantasiapersonajes.es{img_url}"

            return ScrapedOffer(
                product_name=name,
                price=price_val,
                currency="EUR",
                url=url,
                shop_name=self.spider_name,
                is_available=is_avl,
                image_url=img_url
            )
        except Exception as e:
            logger.warning(f"[{self.spider_name}] Direct product page parse error: {e}")
            return None

    def _parse_html_item(self, item) -> Optional[ScrapedOffer]:
        try:
            # 1. Link & Name
            # Site changed h3 to h2 in current structure
            a_tag = item.select_one('h2.product-title a, h3.product-title a, .product-title a')
            if not a_tag: return None
            
            link = a_tag.get('href')
            name = a_tag.get_text(strip=True)
            
            if link and link.startswith('/'):
                 link = f"https://fantasiapersonajes.es{link}"

            # 2. Price (PrestaShop Content Attribute Pattern)
            price_val = 0.0
            # Current display price selector
            price_span = item.select_one('span.product-price, span.price')
            
            if price_span:
                # Try attribute first (very reliable for EUR)
                if price_span.has_attr('content'):
                    try:
                        price_val = float(price_span['content'].replace(',', '.'))
                    except:
                        pass
                
                # Fallback to text cleaning
                if price_val == 0.0:
                    price_val = self._normalize_price(price_span.get_text(strip=True))
            
            if price_val == 0.0:
                # One last attempt: look for meta[itemprop="price"]
                meta_price = item.select_one('meta[itemprop="price"]')
                if meta_price and meta_price.has_attr('content'):
                    try:
                        price_val = float(meta_price['content'].replace(',', '.'))
                    except:
                        pass
            
            if price_val == 0.0:
                logger.debug(f"[{self.spider_name}] Skipping item {name} - Price could not be parsed.")
                return None

            # 3. Availability
            is_avl = True
            
            # Selector-based check (Existing classes)
            if item.select_one('.product-flags .out-of-stock, .product-unavailable, .available-from-date'):
                is_avl = False
            
            # Text-based check (Robustness Kaizen)
            item_text = item.get_text(strip=True).lower()
            if any(term in item_text for term in ["agotado", "no disponible", "reservar", "próximamente", "sin existencias"]):
                is_avl = False
            
            # 4. Image
            img_tag = item.select_one('img')
            img_url = None
            if img_tag:
                 img_url = img_tag.get('data-src') or img_tag.get('src') 
                 if img_url and img_url.startswith('/'):
                     img_url = f"https://fantasiapersonajes.es{img_url}"

            return ScrapedOffer(
                product_name=name,
                price=price_val,
                currency="EUR",
                url=link,
                shop_name=self.spider_name,
                is_available=is_avl,
                image_url=img_url
            )
        except Exception as e:
            logger.warning(f"[{self.spider_name}] Item parsing error: {e}")
            return None

    def _extract_from_json_ld(self, soup) -> List[ScrapedOffer]:
        """
        Attempts to parse schema.org JSON-LD data.
        Looking for @type: ItemList or list of Product.
        """
        import json
        scraped = []
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.get_text(strip=True))
                    
                    # Normalizing list vs dict
                    if isinstance(data, dict):
                        data_list = [data]
                    else:
                        data_list = data
                        
                    for entry in data_list:
                        item_type = entry.get('@type')
                        
                        # Handle "ItemList" which contains "itemListElement"
                        if item_type == 'ItemList' and 'itemListElement' in entry:
                            for pos in entry['itemListElement']:
                                # Sometimes it's just a URL, sometimes a full object
                                item = pos.get('item', {})
                                if item and item.get('@type') == 'Product':
                                    prod = self._parse_json_product(item)
                                    if prod: scraped.append(prod)
                                    
                        # Handle direct "Product"
                        elif item_type == 'Product':
                            prod = self._parse_json_product(entry)
                            if prod: scraped.append(prod)
                            
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"[{self.spider_name}] JSON-LD Error: {e}")
            
        return scraped

    def _parse_json_product(self, data: dict) -> Optional[ScrapedOffer]:
        try:
            name = data.get('name')
            link = data.get('url')
            img_url = data.get('image')
            
            # Ensure URL is absolute
            if img_url and isinstance(img_url, list):
                img_url = img_url[0]
            
            # Price parsing from 'offers'
            offers = data.get('offers', {})
            # It can be a list or dict
            if isinstance(offers, list):
                if not offers: return None
                offers = offers[0]
                
            price = offers.get('price')
            currency = offers.get('priceCurrency', 'EUR')
            status = offers.get('availability', 'InStock')
            
            if not name or not price: return None
            
            is_avl = "InStock" in status
            
            return ScrapedOffer(
                product_name=name,
                price=float(price),
                currency=currency,
                url=link,
                shop_name=self.spider_name,
                is_available=is_avl,
                image_url=img_url
            )
        except Exception:
            return None

    async def _scrape_detail(self, page: Page, url: str) -> dict:
        """
        Fantasia specific: Extract EAN/Referencia.
        """
        if not await self._safe_navigate(page, url):
            return {}
        
        try:
            # Selector from audit: .product-reference span[itemprop="sku"]
            ean_tag = page.locator(".product-reference span[itemprop='sku']")
            if await ean_tag.is_visible(timeout=3000):
                ean = await ean_tag.inner_text()
                return {"ean": ean.strip()}
        except Exception:
            pass
        return {}

    async def _handle_popups(self, page: Page):
        """
        Fantasia specific: Close the 'LOGÍSTICA REYES' modal and accept cookies.
        """
        try:
            # 1. Logistics Modal
            # Based on audit, it has a "CERRAR AVISO" button.
            close_modal = page.locator("button:has-text('CERRAR AVISO'), .modal-header .close")
            if await close_modal.is_visible(timeout=3000):
                logger.info(f"[{self.spider_name}] 📦 Closing Logistics modal...")
                await close_modal.click()
                await asyncio.sleep(0.5)

            # 2. Cookie Banner
            accept_cookies = page.locator("button:has-text('ACEPTO')")
            if await accept_cookies.is_visible(timeout=2000):
                logger.info(f"[{self.spider_name}] 🍪 Accepting cookies...")
                await accept_cookies.click()
                await asyncio.sleep(0.5)
        except Exception:
            pass
