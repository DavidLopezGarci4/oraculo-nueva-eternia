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
            # 2. Lanzar navegador con evasión de automatización estándar y argumentos de seguridad
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # Contexto con User-Agent realista (Chrome 120 para evitar discrepancias TLS)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="es-ES"
            )
            
            page = await context.new_page()
            
            # STEALTH: Inyección de scripts anti-webdriver ligeros (sin romper React/SPA)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { get: () => ['es-ES', 'es', 'en'] });
            """)
            
            cookies_accepted = False
            
            # --- HUMANIZED HOMEPAGE PRE-VISIT ---
            # Navegar primero a la portada para cargar cookies, inicializar retos JS de CloudFront y aceptar consentimiento de forma natural
            self._log("🏠 Navegando a la portada de Wallapop para inicializar cookies y sesión humana...")
            try:
                await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                
                # Validar de forma inmediata si la IP local está greylisted por CloudFront
                cover_content = await page.content()
                if "request could not be satisfied" in cover_content.lower() or "403 error" in cover_content.lower() or "request blocked" in cover_content.lower():
                    self._log("🛡️ Bloqueo de IP detectado (Rate Limit / Greylist de CloudFront) al cargar la portada. Tu IP local está marcada temporalmente por Wallapop. Por favor, espera 10 minutos antes de iniciar otra incursión.", level="warning")
                    self.blocked = True
                    return offers
                    
                accept_btn = page.locator("#onetrust-accept-btn-handler").or_(
                    page.get_by_role("button", name="Aceptar todo")
                ).or_(
                    page.locator("button:has-text('Aceptar')")
                ).first
                
                if await accept_btn.is_visible(timeout=5000):
                    await accept_btn.click()
                    self._log("🍪 Cookies de portada aceptadas (Consentimiento completado).")
                    cookies_accepted = True
                await asyncio.sleep(2)
            except Exception as e:
                # Si falló por timeout de bloqueo, verificar si fue bloqueo
                try:
                    cover_content = await page.content()
                    if "request could not be satisfied" in cover_content.lower() or "403 error" in cover_content.lower() or "request blocked" in cover_content.lower():
                        self._log("🛡️ Bloqueo de IP detectado (Rate Limit / Greylist de CloudFront) al cargar la portada.", level="warning")
                        self.blocked = True
                        return offers
                except:
                    pass
                self._log(f"⚠️ Nota: Error menor precargando portada: {e}", level="warning")
            
            try:
                for search_query, scroll_cycles, click_load_more in queries_config:
                    if self.blocked:
                        self._log("🛡️ Bloqueo detectado. Saltando consultas restantes de Wallapop.", level="warning")
                        break
                        
                    self._log(f"🕵️ Wallapop: Iniciando búsqueda humana para '{search_query}'...")
                    
                    try:
                        # 1. Navegar a la home de Wallapop para establecer contexto seguro y limpio
                        await page.goto(self.base_url, wait_until="networkidle", timeout=40000)
                        await asyncio.sleep(1.5)
                        
                        # Validar si la home devolvió un bloqueo de IP WAF de CloudFront
                        content = await page.content()
                        if "request could not be satisfied" in content.lower() or "403 error" in content.lower() or "request blocked" in content.lower():
                            self._log("🛡️ Bloqueo de IP detectado (Rate Limit / Greylist de CloudFront) en el WAF. Tu IP local está marcada temporalmente. Por favor, espera 10 minutos para que se enfríe.", level="warning")
                            self.blocked = True
                            break
                        
                        # 2. Aceptar Cookies (Consentimiento)
                        try:
                            accept_btn = page.locator("#onetrust-accept-btn-handler").or_(
                                page.get_by_role("button", name="Aceptar todo")
                            ).or_(
                                page.locator("button:has-text('Aceptar')")
                            ).first
                            
                            if await accept_btn.is_visible(timeout=5000):
                                await accept_btn.click()
                                self._log("🍪 Cookies de sesión humana aceptadas.")
                                cookies_accepted = True
                                await asyncio.sleep(1.5)
                        except Exception:
                            pass
                            
                        # 3. Localizar e interactuar con el campo de búsqueda de Wallapop de forma ultra-robusta
                        search_input = page.locator("input[placeholder*='Buscar'], input[name='keywords'], input[type='search']").first
                        try:
                            await search_input.wait_for(state="visible", timeout=15000)
                        except Exception as err:
                            # Diagnóstico visual de error
                            screenshot_path = "C:\\Users\\dace8\\.gemini\\antigravity\\brain\\bb7556b1-2949-4a09-94bc-1223b5dde66f\\scratch\\wallapop_visible_error.png"
                            await page.screenshot(path=screenshot_path)
                            self._log(f"⚠️ No se pudo localizar el campo de búsqueda (visible) de Wallapop: {err}. Captura guardada.", level="warning")
                            continue
                            
                        # Asegurar interacción despejada
                        await search_input.scroll_into_view_if_needed()
                        await search_input.click()
                        await asyncio.sleep(0.5)
                        
                        # Escribir término carácter por carácter con retardos dinámicos realistas
                        for char in search_query:
                            await search_input.type(char, delay=random.randint(40, 110))
                            
                        await asyncio.sleep(0.8)
                        
                        # 4. Pulsar ENTER para detonar la transición SPA de CloudFront
                        await search_input.press("Enter")
                        
                        # 5. Esperar la carga de la página de resultados SPA de forma reactiva
                        try:
                            await page.wait_for_url("**/search*", timeout=15000)
                            self._log(f"🔗 SPA Redirección: Navegado a resultados: {page.url}")
                        except Exception as e:
                            self._log(f"⏳ Nota: Timeout menor esperando URL de búsqueda: {e}", level="warning")
                            
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(2)
                        
                        # 6. Secuencia de Expansión ("Cargar más")
                        if click_load_more:
                            try:
                                await page.keyboard.press("End")
                                await asyncio.sleep(1.2)
                                load_more_btn = page.get_by_role("button", name="Cargar más").or_(page.locator("button:has-text('Cargar más')")).first
                                if await load_more_btn.is_visible(timeout=4000):
                                    await load_more_btn.click()
                                    await page.wait_for_load_state("networkidle")
                                    await asyncio.sleep(1.5)
                            except Exception:
                                pass
                                
                        # 7. Descenso de Scroll dinámico para recolección
                        for i in range(scroll_cycles):
                            await page.mouse.wheel(0, 1500)
                            await asyncio.sleep(0.9)
                            
                        # 8. Extraer y procesar HTML
                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')
                        cards = soup.select("a[href*='/item/']")
                        
                        # 3OX Shield: Detección proactiva y robusta de bloqueos por Cloudflare/CloudFront/CAPTCHA (sin falsos positivos)
                        is_blocked = False
                        if len(cards) == 0:
                            content_lower = content.lower()
                            title_match = re.search(r"<title>(.*?)</title>", content_lower)
                            title_text = title_match.group(1) if title_match else ""
                            
                            if (
                                "attention required" in title_text or
                                "just a moment" in title_text or
                                "request could not be satisfied" in title_text or
                                "cloudflare" in title_text or
                                "forbidden" in title_text or
                                "access denied" in title_text or
                                "security code" in content_lower or
                                "request blocked" in content_lower or
                                len(content) < 45000
                            ):
                                is_blocked = True
                                
                        if is_blocked:
                            self._log("🛡️ Bloqueo detectado (Cloudflare/CloudFront/WAF) al navegar en Wallapop.", level="warning")
                            self.blocked = True
                            break
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
                                clean_href = href.split("?")[0]
                                full_url = clean_href if clean_href.startswith("http") else f"{self.base_url}{clean_href}"
                                
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
