import asyncio
import logging
import random
import time
import re
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
        offers: List[ScrapedOffer] = []
        
        # 1. Configuración inteligente de palabras clave y límites de scroll
        if query == "auto":
            # Estrategia de 2 Consultas de Alta Cobertura (Español + Inglés)
            # Evita bloqueos por navegación consecutiva reiterada y previene timeouts
            queries_config = [
                ("masters del universo", 6, True),   # (query, scroll_cycles, click_load_more) - ¡Alta prioridad en España!
                ("masters of the universe", 4, True)  # Cobertura de términos internacionales
            ]
        else:
            queries_config = [(query, 8, True)]
            
        self._log(f"🌩️ Wallapop Playwright Nexus: Iniciando búsqueda integrada para {len(queries_config)} términos.")
        
        async with async_playwright() as p:
            # 2. Lanzar navegador con evasión de automatización estándar
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # Contexto con User-Agent realista
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent=self._get_random_header()["User-Agent"],
                locale="es-ES"
            )
            
            page = await context.new_page()
            
            # STEALTH: Inyección de scripts anti-webdriver y spoofing de firmas
            await page.add_init_script("""
                // Ocultar webdriver flag
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                
                // Falsear plugins instalados
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                
                // Ocultar variables de automatización de Chrome
                window.chrome = { runtime: {} };
                
                // Spoof de respuesta de permisos
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)
            
            cookies_accepted = False
            
            try:
                for search_query, scroll_cycles, click_load_more in queries_config:
                    if self.blocked:
                        self._log("🛡️ Bloqueo detectado. Saltando consultas restantes de Wallapop.", level="warning")
                        break
                        
                    url = f"{self.base_url}/search?keywords={search_query.replace(' ', '%20')}&order_by=newest"
                    self._log(f"🕵️ Wallapop: Buscando '{search_query}' (Scroll: {scroll_cycles}, Carga: {click_load_more})...")
                    
                    try:
                        # Navegar a la página de resultados
                        await page.goto(url, wait_until="networkidle", timeout=60000)
                        
                        # 3. Aceptar Cookies (Una única vez al iniciar sesión o re-chequeo rápido)
                        if not cookies_accepted:
                            try:
                                accept_btn = page.locator("#onetrust-accept-btn-handler").or_(
                                    page.get_by_role("button", name="Aceptar todo")
                                ).or_(
                                    page.locator("button:has-text('Aceptar')")
                                ).first
                                
                                if await accept_btn.is_visible(timeout=4000):
                                    await accept_btn.click()
                                    self._log("🍪 Cookies aceptadas (Banner de Wallapop despejado).")
                                    cookies_accepted = True
                                    await asyncio.sleep(1)
                            except Exception:
                                pass
                        
                        # 4. Secuencia de Expansión
                        if click_load_more:
                            try:
                                await page.keyboard.press("End")
                                await asyncio.sleep(1)
                                load_more_btn = page.get_by_role("button", name="Cargar más").or_(page.locator("button:has-text('Cargar más')")).first
                                if await load_more_btn.is_visible(timeout=3000):
                                    await load_more_btn.click()
                                    await page.wait_for_load_state("networkidle")
                                    await asyncio.sleep(1.5)
                            except Exception:
                                pass
                                
                        # 5. Descenso de Scroll
                        for i in range(scroll_cycles):
                            await page.mouse.wheel(0, 1500)
                            await asyncio.sleep(0.8)
                            
                        # 6. Extraer y procesar HTML
                        content = await page.content()
                        
                        # 3OX Shield: Detección proactiva de bloqueos por Cloudflare / CloudFront / CAPTCHA
                        if self._detect_block(content) or "cloudflare" in content.lower() or "cloudfront" in content.lower() or "captcha" in content.lower() or "attention required" in content.lower() or "just a moment..." in content.lower() or "security code" in content.lower() or "acceso denegado" in content.lower() or "request could not be satisfied" in content.lower() or "request blocked" in content.lower():
                            self._log("🛡️ Bloqueo detectado (Cloudflare/CloudFront/WAF) al navegar en Wallapop.", level="warning")
                            self.blocked = True
                            break
                            
                        soup = BeautifulSoup(content, 'html.parser')
                        cards = soup.select("a[href*='/item/']")
                        
                        query_offers_count = 0
                        for card in cards:
                            try:
                                price_node = card.select_one("span[class*='Price'], [class*='price']")
                                title_node = card.select_one("p[class*='Title'], [class*='title']")
                                img_node = card.select_one("img")
                                
                                if not price_node or not title_node:
                                    continue
                                    
                                price_text = price_node.get_text(strip=True)
                                price_val = float(re.sub(r'[^\d.,]', '', price_text).replace(',', '.'))
                                
                                if price_val <= 0: continue
                                
                                title = title_node.get_text(strip=True)
                                
                                # Filtro Inteligente de Basura (Excluir ruidos no-figuras/no-reliquias)
                                title_lower = title.lower()
                                junk_keywords = ["camiseta", "t-shirt", "poster", "taza", "mug", "revista", "dvd", "llavero", "keyring", "reproduccion", "repro", "sticker", "pegatina"]
                                if any(kw in title_lower for kw in junk_keywords):
                                    # self._log(f"🗑️ Wallapop: Item descartado por filtro de ruido: '{title}'", level="debug")
                                    continue
                                href = card.get("href", "")
                                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                                
                                image_url = img_node.get("src") if img_node else None
                                
                                # Evitar duplicados del mismo artículo en búsquedas solapadas
                                if any(o.url == full_url for o in offers):
                                    continue
                                    
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
                                query_offers_count += 1
                                
                            except Exception:
                                continue
                                
                        self._log(f"🎁 Wallapop: Halladas {query_offers_count} reliquias para '{search_query}'.")
                        
                        # Retardo respetuoso entre búsquedas de la misma sesión
                        await asyncio.sleep(random.uniform(3.0, 5.0))
                        
                    except Exception as e:
                        self._log(f"⚠️ Error buscando '{search_query}': {e}", level="warning")
                        
            except Exception as e:
                self._log(f"💥 Error crítico general en Wallapop Playwright: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()
                
        self.items_scraped = len(offers)
        self._log(f"✅ Wallapop Complete: Halladas {self.items_scraped} reliquias en total en la superficie.")
        return offers

# Regexp imported at the top

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
