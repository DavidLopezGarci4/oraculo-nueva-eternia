import asyncio
import logging
import random
import time
from typing import List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext
from bs4 import BeautifulSoup
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class WallapopScraper(BaseScraper):
    """
    Scraper de Wallapop basado en Playwright (Phase 43).
    Bypassa bloqueos 403 de CloudFront mediante renderizado real.
    """
    
    def __init__(self):
        super().__init__(shop_name="Wallapop", base_url="https://es.wallapop.com")
        self.is_auction_source = True # Peer-to-Peer
        
    async def search(self, query: str) -> List[ScrapedOffer]:
        search_query = "masters of the universe origins" if query == "auto" else query
        url = f"{self.base_url}/search?keywords={search_query.replace(' ', '%20')}&order_by=newest"
        
        offers: List[ScrapedOffer] = []
        
        self._log(f"🌩️ Wallapop Playwright Nexus: Infiltrando búsqueda: {search_query}")
        
        async with async_playwright() as p:
            # 1. Lanzar navegador con suite de sigilo básica
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent=self._get_random_header()["User-Agent"],
                locale="es-ES"
            )
            page = await context.new_page()
            
            try:
                # 2. Navegar a Wallapop
                self._log(f"🧭 Navegando a resultados: {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # 3. Gestionar Cookies (Aceptar si aparece el banner)
                try:
                    # Intentamos varios selectores comunes (OneTrust / Texto)
                    accept_btn = page.locator("#onetrust-accept-btn-handler").or_(
                        page.get_by_role("button", name="Aceptar todo")
                    ).or_(
                        page.locator("button:has-text('Aceptar')")
                    ).first
                    
                    if await accept_btn.is_visible(timeout=5000):
                        await accept_btn.click()
                        self._log("🍪 Cookies aceptadas (Banner despejado).")
                        await asyncio.sleep(1)
                except Exception as e:
                    self._log(f"ℹ️ No se detectó banner de cookies o ya fue gestionado.")

                # 4. Fase de Expansión Maestra (Phase 43.1)
                self._log("🧬 Iniciando secuencia de expansión profunda...")
                
                # Paso 4a: Scroll inicial para que aparezca el botón "Cargar más"
                await page.keyboard.press("End")
                await asyncio.sleep(2)

                # Paso 4b: El Click Maestro (Botón turquesa)
                # Buscamos el botón por texto para mayor precisión
                try:
                    # Selector basado en el texto del botón
                    load_more_btn = page.get_by_role("button", name="Cargar más").or_(page.locator("button:has-text('Cargar más')")).first
                    if await load_more_btn.is_visible():
                        self._log("🖱️ Botón 'Cargar más' detectado. Ejecutando click de expansión.")
                        await load_more_btn.click()
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(2)
                except Exception as e:
                    self._log(f"ℹ️ No se pudo pulsar 'Cargar más': {e}")

                # Paso 4c: Descenso Profundo (Infinite Scroll)
                self._log("🧭 Iniciando bucle de scroll infinito (Descenso Profundo)...")
                for i in range(8):  # 8 ciclos de scroll
                    await page.mouse.wheel(0, 1500)
                    await asyncio.sleep(0.8)
                    if i % 3 == 0:
                        self._log(f"  - Nivel {i+1} de profundidad alcanzado.")

                # 5. Extraer contenido HTML final expandido
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 6. Parsing de items (Selectores refinados)
                # Capturamos todos los links que parezcan items
                cards = soup.select("a[href*='/item/']")
                
                self._log(f"🔎 Analizando {len(cards)} posibles reliquias...")
                
                for card in cards:
                    try:
                        # Extraer título y precio
                        # El precio suele estar en un span con clase price
                        price_node = card.select_one("span[class*='Price'], [class*='price']")
                        title_node = card.select_one("p[class*='Title'], [class*='title']")
                        img_node = card.select_one("img")
                        
                        if not price_node or not title_node:
                            continue
                            
                        # Limpiar precio
                        price_text = price_node.get_text(strip=True)
                        price_val = float(re.sub(r'[^\d.,]', '', price_text).replace(',', '.'))
                        
                        if price_val <= 0: continue
                        
                        title = title_node.get_text(strip=True)
                        href = card.get("href", "")
                        full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                        
                        image_url = img_node.get("src") if img_node else None
                        
                        offer = ScrapedOffer(
                            product_name=title,
                            price=price_val,
                            url=full_url,
                            shop_name=self.shop_name,
                            image_url=image_url,
                            source_type="Peer-to-Peer",
                            sale_type="Fixed_P2P"
                        )
                        offers.append(offer)
                        
                    except Exception as e:
                        continue
                
                self.items_scraped = len(offers)
                self._log(f"✅ Wallapop: Halladas {len(offers)} reliquias en la superficie.")
                
            except Exception as e:
                self._log(f"💥 Error crítico en Wallapop Playwright: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()
                
        return offers

# Import regexp for price cleaning
import re

if __name__ == "__main__":
    import sys
    import io
    # [3OX] Unicode Resilience
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    
    # Enable logging to see _log output
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    async def test():
        scraper = WallapopScraper()
        results = await scraper.search("masters of the universe origins")
        print(f"\n--- RESULTADOS FINALES ---")
        print(f"Total items hallados: {len(results)}")
        for r in results[:10]:
            print(f"- {r.product_name}: {r.price}€ -> {r.url}")
            
    asyncio.run(test())
