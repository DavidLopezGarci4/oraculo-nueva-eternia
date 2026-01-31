import asyncio
import os
import logging
import re
import io
import sys
import random
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import Page, BrowserContext
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

# Force UTF-8 for console output to handle emojis safely
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

logger = logging.getLogger(__name__)

class AmazonScraper(BaseScraper):
    """
    Amazon Spain Scraper for Masters of the Universe: Origins.
    Optimized for amazon.es with anti-bot measures.
    """
    def __init__(self):
        super().__init__(shop_name="Amazon.es", base_url="https://www.amazon.es")
        self.search_url = "https://www.amazon.es/s?k="

    async def search(self, query: str) -> List[ScrapedOffer]:
        """
        Searches Amazon.es for MOTU Origins items.
        Uses stealthy curl-cffi for initial infiltration, bypassing Playwright detection.
        """
        search_query = "masters of the universe origins" if query == "auto" else query
        url = f"{self.search_url}{search_query.replace(' ', '+')}"
        self.blocked = False # Reset block status for new attempt
        
        self._log(f"🕸️ Amazon.es: Infiltrando búsqueda para '{search_query}' vía curl-cffi...")
        
        offers = []
        html = await self._curl_get(url)
        
        if not html:
            self._log("❌ Amazon.es: No se pudo obtener HTML vía curl-cffi. Intentando fallback táctico...", level="warning")
            return await self._search_playwright_fallback(url)

        self._log(f"📄 Amazon.es: Recibidos {len(html)} bytes. Analizando estructura...")
        soup = BeautifulSoup(html, "html.parser")
        
        # Detect block in soup too
        if "captcha" in html.lower() or "robot" in html.lower():
            self._log("🚫 Amazon.es: Bloqueado por CAPTCHA en curl-cffi. Intentando fallback táctico (Playwright)...", level="warning")
            return await self._search_playwright_fallback(url)

        # Extract results - More robust selection
        # [data-asin] is the most consistent marker for a product card
        results = soup.select("[data-asin]")
        if not results:
            results = soup.select(".s-result-item")
        
        self._log(f"📊 Amazon.es: Detectados {len(results)} bloques con [data-asin].")

        for res in results:
            asin = res.get("data-asin")
            if not asin or len(asin) != 10:
                continue # Skip non-product items (banners, etc)

            try:
                # Title - Try multiple common classes
                title = "Unknown"
                title_el = (
                    res.select_one("h2 a span") or 
                    res.select_one(".a-size-medium.a-color-base.a-text-normal") or
                    res.select_one(".a-size-base-plus.a-color-base.a-text-normal") or
                    res.select_one("h2")
                )
                if title_el:
                    title = title_el.get_text(strip=True)
                
                # Price - Robust extraction
                price = 0.0
                price_el = (
                    res.select_one(".a-price .a-offscreen") or
                    res.select_one(".a-price-whole") or
                    res.select_one(".a-color-price")
                )
                if price_el:
                    price = self._normalize_price(price_el.get_text())

                # URL
                link_el = res.select_one("a.a-link-normal") or res.select_one("h2 a")
                relative_url = link_el.get("href") if link_el else ""
                
                # Clean URL (remove refs)
                if relative_url:
                    full_url = f"https://www.amazon.es{relative_url.split('/ref=')[0]}"
                else:
                    full_url = f"https://www.amazon.es/dp/{asin}"
                
                # Image
                img_el = res.select_one("img.s-image")
                image_url = img_el.get("src") if img_el else None

                if price > 0:
                    offers.append(ScrapedOffer(
                        product_name=title,
                        price=price,
                        url=full_url,
                        shop_name=self.shop_name,
                        image_url=image_url,
                        source_type="Retail"
                    ))
                    self.items_scraped += 1
                else:
                    # Log if we found a product but no price (common block symptom)
                    if title != "Unknown":
                        self._log(f"🕵️ Amazon.es: Producto '{title[:30]}...' hallado pero sin precio.", level="debug")

            except Exception as e:
                continue
        
        if not offers:
            title_tag = soup.title.string if soup.title else "No Title"
            self._log(f"⚠️ Amazon.es: 0 ofertas extraídas. Título página: '{title_tag}'", level="warning")
            snippet = html[:500].replace('\n', ' ')
            self._log(f"🔍 Snippet: {snippet}...", level="debug")
            
            if results:
                self._log("⚠️ Amazon.es: Se detectaron bloques pero no se extrajeron ofertas válidas (¿Selector de precio/título roto?).", level="warning")

        return offers

    async def _search_playwright_fallback(self, url: str) -> List[ScrapedOffer]:
        """Original Playwright logic kept as emergency fallback."""
        self._log(f"⚠️ Amazon.es: Ejecutando fallback de Playwright para {url}...", level="warning")
        offers = []
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                # STEALTH: Anti-detection flags
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--window-size=1920,1080'
                    ]
                )
                
                # Contexto con fingerprint español realista
                context = await browser.new_context(
                    user_agent=self._get_random_header()["User-Agent"],
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-ES',
                    timezone_id='Europe/Madrid',
                    permissions=['geolocation']
                )
                
                # Headers adicionales anti-bloqueo (Simulando Chrome 120+ en Windows)
                await context.set_extra_http_headers({
                    'Accept-Language': 'es-ES,es;q=0.9',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Service-Worker-Navigation-Preload': 'true'
                })

                page = await context.new_page()
                
                # Inyectar scripts avanzados para evadir detección de automatización profunda (Stealth 3.0)
                await page.add_init_script("""
                    // 1. Hide WebDriver and Automation
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {}, app: {}, loadTimes: {}, csi: {} };
                    
                    // 2. Mock Hardware and Environment
                    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                    Object.defineProperty(navigator, 'languages', { get: () => ['es-ES', 'es'] });
                    
                    // 3. Robust WebGL Fingerprint
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) return 'Intel Inc.';
                        if (parameter === 37446) return 'Intel(R) Iris(R) Xe Graphics';
                        return getParameter.apply(this, arguments);
                    };
                    
                    // 4. Overwrite broken/missing properties
                    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });
                    
                    // 5. Mock Permissions (Fixing broken browser prompt detection)
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                    );
                """)
                
                success = await self._safe_navigate(page, url)
                if not success:
                    self._log("❌ Amazon.es: Fallback de Playwright bloqueado o error de navegación.", level="error")
                    if not os.path.exists("logs/screenshots"): os.makedirs("logs/screenshots")
                    await page.screenshot(path="logs/screenshots/amazon_nav_fail_fallback.png")
                    await browser.close()
                    return []

                # Handle Cookie Banner
                try:
                    cookie_btn = await page.query_selector("#sp-cc-accept")
                    if cookie_btn:
                        await cookie_btn.click()
                        await asyncio.sleep(1)
                except Exception:
                    pass

                # Wait for results to load with block detection (Increased timeout to 30s)
                try:
                    # Selector ampliado para mayor robustez
                    await page.wait_for_selector("[data-component-type='s-search-result'], [data-asin]", timeout=30000)
                except Exception:
                    # Check if blocked by captcha or similar
                    content = await page.content()
                    if "sp-cc-accept" in content and "captcha" not in content.lower():
                        self._log("⚠️ Amazon.es: Resultados no cargan pero el banner de cookies está presente. Intentando scroll...", level="warning")
                        await page.evaluate("window.scrollBy(0, 500)")
                        await asyncio.sleep(2)
                    elif "captcha" in content.lower() or "robot" in content.lower() or "api-services-support" in content.lower():
                        self._log("🚫 Amazon.es: Bot detectado (CAPTCHA/ROBOT) en fallback de Playwright.", level="error")
                        self.blocked = True
                        if not os.path.exists("logs/screenshots"): os.makedirs("logs/screenshots")
                        await page.screenshot(path="logs/screenshots/amazon_captcha_fallback.png")
                        await browser.close()
                        return []
                    else:
                        self._log("❌ Amazon.es: Timeout esperando resultados tras 30s en fallback de Playwright.", level="error")
                        if not os.path.exists("logs/screenshots"): os.makedirs("logs/screenshots")
                        await page.screenshot(path="logs/screenshots/amazon_timeout_fallback.png")
                        await browser.close()
                        return []

                # --- HUMAN BEHAVIOR: Randomized vertical scroll-and-pause ---
                # This makes Amazon think a human is looking at the search results.
                scroll_steps = random.randint(2, 4)
                for _ in range(scroll_steps):
                    scroll_y = random.randint(300, 700)
                    await page.evaluate(f"window.scrollBy(0, {scroll_y})")
                    await self._random_sleep(0.8, 2.2)
                
                # Extract results (Multiple selectors for agility)
                results = await page.query_selector_all("[data-component-type='s-search-result']")
                if not results:
                    results = await page.query_selector_all(".s-result-item[data-asin]")
                
                self._log(f"📊 Amazon.es: Encontrados {len(results)} posibles resultados con Playwright fallback.")

                for res in results:
                    try:
                        # Title extraction - Simple and effective
                        title = "Unknown"
                        title_el = await res.query_selector("h2")
                        if title_el:
                            title = await title_el.text_content()
                            title = title.strip() if title else "Unknown"
                        
                        # Price extraction
                        price = 0.0
                        price_el = await res.query_selector(".a-price .a-offscreen")
                        if price_el:
                            price_text = await price_el.text_content()
                            price = self._normalize_price(price_text)
                        
                        if price == 0:
                            # Try fallback legacy selector
                            price_whole = await res.query_selector(".a-price-whole")
                            if price_whole:
                                p_whole = await price_whole.text_content()
                                price = self._normalize_price(p_whole)

                        # URL & ASIN extraction
                        link_el = await res.query_selector("a.a-link-normal")
                        if not link_el:
                            link_el = await res.query_selector("h2 a")
                        
                        relative_url = await link_el.get_attribute("href") if link_el else ""
                        full_url = f"https://www.amazon.es{relative_url.split('/ref=')[0]}" if relative_url else ""
                        
                        # ASIN recovery
                        asin_match = re.search(r'/dp/([A-Z0-9]{10})', full_url)
                        asin = asin_match.group(1) if asin_match else None
                        
                        if not asin:
                            # Try to find data-csa-c-item-id (found in debug log)
                            container = await res.query_selector("[data-csa-c-item-id]")
                            if container:
                                attr = await container.get_attribute("data-csa-c-item-id")
                                if attr and "asin.1." in attr:
                                    asin = attr.split("asin.1.")[1]
                                    if not full_url:
                                        full_url = f"https://www.amazon.es/dp/{asin}"

                        # Image
                        img_el = await res.query_selector("img.s-image")
                        image_url = await img_el.get_attribute("src") if img_el else None

                        if price > 0 and asin:
                            offers.append(ScrapedOffer(
                                product_name=title,
                                price=price,
                                url=full_url,
                                shop_name=self.shop_name,
                                image_url=image_url,
                                ean=None, # Amazon doesn't show EAN in search, need detail page
                                source_type="Retail"
                            ))
                            self.items_scraped += 1

                    except Exception as e:
                        self._log(f"⚠️ Error procesando resultado de Amazon (Playwright fallback): {e}", level="warning")
                        continue

                await browser.close()
                
        except Exception as e:
            self._log(f"❌ Fallo crítico en AmazonScraper (Playwright fallback): {e}", level="error")
            self.errors += 1
        
        return offers
