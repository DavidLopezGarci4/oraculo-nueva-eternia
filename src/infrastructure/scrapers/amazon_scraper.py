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
        Evolved Strategy (Sirius A1): 
        1. Try curl-cffi for fast infiltration.
        2. If blocked or 0 items, escalate to Playwright with Human Interaction (Session Legitimization).
        """
        search_query = "masters of the universe origins" if query == "auto" else query
        url = f"{self.search_url}{search_query.replace(' ', '+')}"
        self.blocked = False
        
        self._log(f"🕸️ Amazon.es: Iniciando incursión para '{search_query}'...")
        
        # Phase 1: Fast Infiltration (curl-cffi)
        offers = await self._fast_infiltration(url, search_query)
        
        # Phase 2: Tactical Escalation (Playwright Human-Like)
        if not offers or self.blocked:
            self._log(f"⚠️ Amazon.es: Infiltración rápida fallida o bloqueada. Escalamiento a Sirius A1 (Buscador Humano)...", level="warning")
            offers = await self._sirius_a1_human_search(search_query)
        
        return offers

    async def _fast_infiltration(self, url: str, search_query: str) -> List[ScrapedOffer]:
        """Attempt fast extraction via curl-cffi."""
        offers = []
        html = await self._curl_get(url, impersonate="chrome120")
        
        if not html:
            return []

        if "captcha" in html.lower() or "robot" in html.lower() or "api-services-support" in html.lower():
            self._log("🛡️ Amazon.es: Bloqueo detectado en curl-cffi (CAPTCHA/503).", level="debug")
            self.blocked = True
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = soup.select("[data-asin]")
        
        for res in results:
            asin = res.get("data-asin")
            if not asin or len(asin) != 10: continue

            try:
                title_el = res.select_one("h2 a span") or res.select_one(".a-size-medium")
                title = title_el.get_text(strip=True) if title_el else "Unknown"
                
                price_el = res.select_one(".a-price .a-offscreen") or res.select_one(".a-price-whole")
                price = self._normalize_price(price_el.get_text()) if price_el else 0.0

                if price > 0:
                    link_el = res.select_one("a.a-link-normal")
                    rel_url = link_el.get("href") if link_el else f"/dp/{asin}"
                    full_url = f"https://www.amazon.es{rel_url.split('/ref=')[0]}"
                    
                    img_el = res.select_one("img.s-image")
                    image_url = img_el.get("src") if img_el else None

                    offers.append(ScrapedOffer(
                        product_name=title, price=price, url=full_url,
                        shop_name=self.shop_name, image_url=image_url, source_type="Retail"
                    ))
            except: continue
            
        return offers

    async def _sirius_a1_human_search(self, search_query: str) -> List[ScrapedOffer]:
        """
        Ultra-Resilient Human-Like Search Strategy.
        1. Navigate to Home
        2. Accept Cookies
        3. Type in search bar with delays
        4. Scroll and extract
        """
        offers = []
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
                )
                
                context = await browser.new_context(
                    user_agent=self._get_random_header()["User-Agent"],
                    viewport={'width': 1920, 'height': 1080},
                    locale='es-ES'
                )
                
                # Enhanced Stealth
                await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                page = await context.new_page()
                
                # 1. Navigate to Home (Legitimization)
                self._log(f"🏠 Amazon.es: Legitimando sesión en la Home...")
                await page.goto("https://www.amazon.es", wait_until="domcontentloaded", timeout=45000)
                await self._random_sleep(1, 2)
                
                # 2. Accept Cookies
                try:
                    cookie_btn = await page.wait_for_selector("#sp-cc-accept", timeout=5000)
                    if cookie_btn:
                        self._log("🍪 Amazon.es: Aceptando cookies...")
                        await cookie_btn.click()
                        await self._random_sleep(0.5, 1.5)
                except:
                    pass
                
                # 3. Type Search Term (Human Interaction)
                self._log(f"⌨️ Amazon.es: Escribiendo '{search_query}' letra a letra...")
                search_box = await page.wait_for_selector("#twotabsearchtextbox", timeout=10000)
                if not search_box:
                    self._log("❌ Amazon.es: No se encontró el cuadro de búsqueda.", level="error")
                    await browser.close()
                    return []
                
                await search_box.click()
                for char in search_query:
                    await page.keyboard.type(char)
                    await asyncio.sleep(random.uniform(0.05, 0.2))
                
                await page.keyboard.press("Enter")
                self._log("🔍 Amazon.es: Búsqueda enviada. Esperando resultados...")
                
                # 4. Wait for results with adaptive timeout
                try:
                    await page.wait_for_selector("[data-component-type='s-search-result']", timeout=20000)
                except Exception:
                    # Check for CAPTCHA at this stage too
                    content = await page.content()
                    if "captcha" in content.lower() or "robot" in content.lower():
                        self._log("🚫 Amazon.es: CAPTCHA detectado tras búsqueda humana.", level="error")
                        if not os.path.exists("logs/screenshots"): os.makedirs("logs/screenshots")
                        await page.screenshot(path="logs/screenshots/amazon_sirius_captcha.png")
                        await browser.close()
                        return []
                    self._log("⚠️ Amazon.es: Sin resultados visibles tras 20s. Probando extracción de emergencia...", level="warning")

                # 5. Extraction Loop with Pagination
                current_page = 1
                max_pages = 2 # Target ~50+ items (Amazon usually has ~24 per page)
                all_offers = []
                
                while current_page <= max_pages:
                    self._log(f"📄 Amazon.es: Procesando página {current_page}...")
                    
                    # Deep Human-like Scroll to trigger lazy loading
                    for i in range(3):
                        scroll_y = 1000
                        await page.evaluate(f"window.scrollBy(0, {scroll_y})")
                        self._log(f"⏬ Amazon.es: Scroll profundo ({i+1}/3)...", level="debug")
                        await self._random_sleep(1.0, 2.0)
                    
                    # Extract from current page
                    page_results = await page.query_selector_all("[data-asin]")
                    self._log(f"📊 Amazon.es: Detectados {len(page_results)} bloques en página {current_page}.")

                    for res in page_results:
                        try:
                            asin = await res.get_attribute("data-asin")
                            if not asin or len(asin) != 10: continue

                            # Title
                            title_el = await res.query_selector("h2")
                            title = await title_el.text_content() if title_el else "Unknown"
                            title = title.strip() if title else "Unknown"
                            
                            # Price
                            price_el = await res.query_selector(".a-price .a-offscreen")
                            price = self._normalize_price(await price_el.text_content()) if price_el else 0.0

                            if price > 0:
                                link_el = await res.query_selector("h2 a") or await res.query_selector("a.a-link-normal")
                                rel_url = await link_el.get_attribute("href") if link_el else f"/dp/{asin}"
                                full_url = f"https://www.amazon.es{rel_url.split('/ref=')[0]}"
                                
                                img_el = await res.query_selector("img.s-image")
                                image_url = await img_el.get_attribute("src") if img_el else None

                                # Deduplicate by URL
                                if not any(o.url == full_url for o in all_offers):
                                    all_offers.append(ScrapedOffer(
                                        product_name=title, price=price, url=full_url,
                                        shop_name=self.shop_name, image_url=image_url, source_type="Retail"
                                    ))
                                    self.items_scraped += 1
                        except:
                            continue

                    if current_page >= max_pages:
                        break

                    # Tactical Page Flip
                    try:
                        self._log("↪️ Amazon.es: Intentando pasar a la siguiente página...")
                        next_btn = await page.query_selector("a.s-pagination-next, .s-pagination-next")
                        if next_btn and await next_btn.is_visible():
                            await next_btn.click()
                            await page.wait_for_load_state("domcontentloaded")
                            await self._random_sleep(2, 4)
                            current_page += 1
                        else:
                            self._log("🏁 Amazon.es: No se encontró botón 'Siguiente' o es el final.")
                            break
                    except Exception as e:
                        self._log(f"⚠️ Error al paginar: {e}", level="warning")
                        break

                await browser.close()
                self._log(f"✅ Amazon.es: Extracción Sirius A1 completada con {len(all_offers)} ofertas totales.")
                return all_offers
                
        except Exception as e:
            self._log(f"❌ Fallo crítico en Sirius A1: {e}", level="error")
            self.errors += 1
        
        return offers

if __name__ == "__main__":
    # Test block for internal verification
    async def test():
        scraper = AmazonScraper()
        results = await scraper.search("auto")
        print(f"\n--- RESULTADOS ({len(results)}) ---")
        for res in results[:5]:
            print(f"[{res.shop_name}] {res.product_name} - {res.price}{res.currency}")
    
    asyncio.run(test())
