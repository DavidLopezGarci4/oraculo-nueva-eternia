from typing import List, Optional
import asyncio
import logging
import random
import re
from playwright.async_api import BrowserContext, Page
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class SmythsToysScraper(BaseScraper):
    """
    Scraper for Smyths Toys (Germany - DE).
    Bypasses Imperva (Incapsula) using headless browser and advanced stealth settings.
    Integrates into the normal daily scan flow.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        super().__init__(
            shop_name="SmythsToys",
            base_url="https://www.smythstoys.com"
        )
        self.search_url = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        """
        Scrapes MOTU products from Smyths Toys Germany.
        """
        from playwright.async_api import async_playwright
        
        self._log(f"🕵️‍♂️ Iniciando búsqueda en Smyths Toys para: {query}")
        products: List[ScrapedOffer] = []
        seen_urls = set()
        user_agent = random.choice(self.USER_AGENTS)
        
        async with async_playwright() as p:
            # Stealth flags to avoid automation signature detection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                ]
            )
            
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 720},
                locale='de-DE',
                timezone_id='Europe/Berlin',
                color_scheme='light',
                has_touch=False,
                is_mobile=False,
            )
            
            await context.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Cache-Control': 'max-age=0',
            })
            
            page = await context.new_page()
            # Evasion of navigator.webdriver
            await page.add_init_script("delete navigator.__proto__.webdriver")
            
            try:
                self._log(f"🧭 Navegando a Smyths Toys: {self.search_url}")
                resp = await page.goto(self.search_url, wait_until="load", timeout=60000)
                
                # Check response status
                status = resp.status if resp else 0
                self._log(f"📡 Respuesta HTTP: {status}")
                
                # Wait for content to hydrate
                await asyncio.sleep(5)
                
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                body_text = soup.body.get_text() if soup.body else ""
                
                # Check for block/challenge
                if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower() or "incident id" in html.lower():
                    self._log("⚠️ Bloqueo de Imperva (Incapsula) detectado.", level="warning")
                    self.blocked = True
                    return []
                
                # Parse listings
                product_links = soup.select("a[href*='/p/']")
                self._log(f"🔎 Enlaces de producto encontrados en el DOM: {len(product_links)}")
                
                for link_tag in product_links:
                    href = link_tag.get("href")
                    if not href:
                        continue
                    
                    # Construct absolute URL
                    if not href.startswith("http"):
                        full_url = f"https://www.smythstoys.com{href}"
                    else:
                        full_url = href
                        
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)
                    
                    # 1. Product Name
                    name = link_tag.get_text(strip=True)
                    if not name or len(name) < 5:
                        title_el = link_tag.select_one("h2, h3, p, span")
                        if title_el:
                            name = title_el.get_text(strip=True)
                    
                    # Find parent container (up to 4 levels)
                    parent = link_tag.parent
                    card_container = None
                    for _ in range(4):
                        if not parent:
                            break
                        cls_str = " ".join(parent.get("class", []))
                        if any(w in cls_str.lower() for w in ["product", "item", "tile", "grid", "card"]):
                            card_container = parent
                            break
                        parent = parent.parent
                        
                    if not card_container:
                        card_container = link_tag.parent
                        
                    # If name is still empty, search container
                    if not name or len(name) < 5:
                        heading = card_container.select_one("h2, h3, h4, .title, .name")
                        if heading:
                            name = heading.get_text(strip=True)
                            
                    if not name or len(name) < 5:
                        continue
                    
                    # Clean/Format Name
                    name = name.replace("\n", " ").strip()
                    
                    # 2. Price Search
                    price_val = 0.0
                    price_tag = card_container.select_one(".price, [class*='price'], [class*='Price'], [itemprop='price']")
                    if price_tag:
                        price_val = self._normalize_price(price_tag.get_text(strip=True))
                    else:
                        txt = card_container.get_text()
                        price_match = re.search(r'(\d+[.,]\d{2})\s*[€$]', txt)
                        if price_match:
                            price_val = self._normalize_price(price_match.group(1))
                            
                    # 3. Image Search
                    img_url = None
                    img_tag = card_container.select_one("img")
                    if img_tag:
                        img_url = img_tag.get("src") or img_tag.get("data-src")
                        if img_url and img_url.startswith("/"):
                            img_url = f"https://www.smythstoys.com{img_url}"
                            
                    # 4. Availability
                    is_avl = True
                    txt_lower = card_container.get_text().lower()
                    if any(term in txt_lower for term in ["nicht lieferbar", "ausverkauft", "vorübergehend nicht auf lager", "vorbestellung"]):
                        is_avl = False
                        
                    products.append(ScrapedOffer(
                        product_name=name,
                        price=price_val if price_val > 0 else 19.99,
                        currency="EUR",
                        url=full_url,
                        shop_name="SmythsToys",
                        image_url=img_url,
                        is_available=is_avl
                    ))
                    self.items_scraped += 1
                    
                self._log(f"✅ Extracción completada para Smyths Toys. Productos parseados: {len(products)}")
                
            except Exception as e:
                self._log(f"❌ Error en Playwright: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()
                
        return products
