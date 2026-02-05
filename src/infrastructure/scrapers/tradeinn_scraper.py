import asyncio
import sys
import io
from typing import List
from playwright.async_api import async_playwright
from .base import BaseScraper, ScrapedOffer
import logging

# [3OX] Unicode Resilience Shield
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = logging.getLogger(__name__)

class TradeinnScraper(BaseScraper):
    """
    Scraper for Tradeinn (and its sub-stores like Kidinn, Diveinn, etc.)
    Uses Playwright to handle Algolia's dynamic rendering.
    """
    def __init__(self):
        super().__init__(shop_name="Tradeinn", base_url="https://www.tradeinn.com")
        self.search_url = "https://www.tradeinn.com/es/busqueda?q="

    async def search(self, query: str) -> List[ScrapedOffer]:
        self._log(f"🔍 Iniciando incursión en Tradeinn para: {query}")
        results = []
        
        async with async_playwright() as p:
            # We use stealthy arguments to avoid easy detection
            browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            # stealth script
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = await context.new_page()
            
            # [3OX] Paso 1: Establecer sesión en Home para evitar redirección de deep-linking
            self._log(f"🌩️ Estableciendo sesión de confianza en {self.base_url}...")
            try:
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(2)
                
                # Aceptar cookies (Crucial para que carguen scripts de terceros como Algolia/ReCaptcha)
                accept_btn = page.locator('button:has-text("Aceptar todas las cookies")')
                if await accept_btn.is_visible(timeout=5000):
                    await accept_btn.click()
                    self._log("🍪 Cookies aceptadas. Sesión legitimada.")
                    await asyncio.sleep(1)
            except Exception as e:
                self._log(f"⚠️ Aviso: Error estableciendo sesión: {str(e)[:50]}")

            # [3OX] Paso 2: Estrategia de Búsqueda de tres fases
            # Fase A: URL Directa en Tradeinn
            url = f"{self.base_url}/es/busqueda?q={query.replace(' ', '+')}"
            self._log(f"🧭 Intentando acceso directo Tradeinn: {url}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4) # Tiempo para que Algolia despierte
                
                # Intentar detectar si hay resultados en la URL directa
                if await page.locator('li.js-content-buscador_li').count() > 0:
                    self._log("✅ Acceso directo Tradeinn exitoso.")
                else:
                    self._log("🔄 Tradeinn redirigido o sin resultados inmediatos. Probando Kidinn Fallback...")
                    # Fase B: Kidinn (Mismo motor, a veces menos protegido para direct urls)
                    kidinn_url = f"https://www.tradeinn.com/kidinn/es/busqueda?q={query.replace(' ', '+')}"
                    await page.goto(kidinn_url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(4)
                    
                    if await page.locator('li.js-content-buscador_li').count() > 0:
                        self._log("✅ Acceso Kidinn exitoso.")
                    else:
                        self._log("🔄 Kidinn redirigido. Iniciando Fase C: Interacción Humana Profunda...")
                        # Fase C: Interacción en la Home (Último recurso, muy resiliente)
                        if page.url != self.base_url:
                            await page.goto(self.base_url, wait_until="domcontentloaded", timeout=45000)
                        
                        # 1. Asegurar foco y limpiar
                        search_box = page.locator('#buscador_google')
                        await search_box.scroll_into_view_if_needed()
                        await search_box.click()
                        await asyncio.sleep(0.5)
                        
                        # 2. Escritura carácter por carácter (Simulación humana real)
                        await page.keyboard.down("Control") # Limpieza preventiva
                        await page.keyboard.press("a")
                        await page.keyboard.up("Control")
                        await page.keyboard.press("Backspace")
                        
                        await page.keyboard.type(query, delay=150)
                        await asyncio.sleep(1)
                        
                        # 3. Disparar búsqueda (Enter + Click Fallback)
                        await page.keyboard.press("Enter")
                        self._log("🚀 Búsqueda enviada vía Enter.")
                        
                        # Fallback click si no detectamos cambio de estado en 3 segundos
                        await asyncio.sleep(3)
                        if not await page.locator('#js-content-buscador_ol').is_visible():
                            search_icon = page.locator('#buscador_google_container img.icon-search').first
                            if await search_icon.is_visible():
                                self._log("🖱️ Enter fallido o lento, usando Click en lupa...")
                                await search_icon.click()
                        
                        # Espera generosa por el contenedor de Algolia
                        await asyncio.sleep(5)
            except Exception as e:
                self._log(f"⚠️ Error en estrategia de búsqueda: {str(e)[:50]}", level="warning")

            # [3OX] Paso 3: Verificación Final de Resultados (Algolia Container)
            try:
                # El contenedor #js-content-buscador_ol es donde Algolia inyecta los hits
                await page.wait_for_selector('#js-content-buscador_ol', timeout=25000)
                # Esperar un momento extra para que se pueble
                await asyncio.sleep(2)
            except Exception:
                if await page.locator('#js-no_result_buscador').is_visible():
                    self._log("ℹ️ No se encontraron resultados para la búsqueda.")
                    await browser.close()
                    return []
                else:
                    self._log("⚠️ No se detectan productos. Capturando estado...", level="warning")
                    await page.screenshot(path="tradeinn_final_failover.png")
                    await browser.close()
                    return []
            
            items_selector = 'li.js-content-buscador_li'

            # 4. Extract data
            items = await page.locator(items_selector).all()
            self._log(f"📦 Detectados {len(items)} items. Procesando...")
            
            for item in items[:40]: # Process up to 40 results
                try:
                    product = await self._get_product_details(item)
                    if product:
                        results.append(ScrapedOffer(
                            product_name=product['name'],
                            price=product['price'],
                            url=product['url'],
                            shop_name=product['shop_name'],
                            image_url=product['image_url'],
                            is_available=product.get('is_available', True)
                        ))
                except Exception as e:
                    logger.debug(f"Error parseando reliquia en Tradeinn: {e}")
                    continue
            
            await browser.close()
            self._log(f"✅ Incursión finalizada. {len(results)} ofertas recolectadas.")
            return results

    async def _get_product_details(self, card) -> dict:
        """Extracts individual product details from a card."""
        try:
            # Selectores robustos basados en el debug HTML
            name_el = card.locator('p#js-nombre_producto_listado')
            # Current price selector
            price_el = card.locator('p.js-precio_producto')
            # Previous price selector (discount indicator)
            old_price_el = card.locator('p.js-precio_producto_anterior')
            
            link_el = card.locator('a.js-href_list_products')
            img_el = card.locator('img.js-image_list_product')
            
            if await name_el.count() == 0 or await link_el.count() == 0:
                return None

            name = await name_el.inner_text()
            price_raw = await price_el.inner_text() if await price_el.count() > 0 else "0"
            link = await link_el.get_attribute('href')
            image_url = await img_el.get_attribute('src') or await img_el.get_attribute('data-src')

            if not link: return None

            # [3OX] Distribución de sub-tiendas (Kidinn, Diveinn, etc.)
            shop_name = "Tradeinn"
            parts = link.strip('/').split('/')
            if len(parts) > 0 and parts[0] != "es":
                shop_name = f"Tradeinn ({parts[0].capitalize()})"
            
            # [3OX] Tradeinn Availability Logic: 
            # Si aparece en la lista, normalmente está disponible, pero chequeamos indicadores visuales
            is_available = True
            if await price_el.count() == 0 or price_raw.strip() == "":
                is_available = False
            
            # Robustness check for specific out-of-stock text in the card
            item_text = (await card.inner_text()).lower()
            if any(term in item_text for term in ["agotado", "no disponible", "avísame", "unavailable"]):
                is_available = False
            
            price = self._normalize_price(price_raw)
            
            return {
                'name': name.strip(),
                'price': price,
                'url': link if link.startswith('http') else f"https://www.tradeinn.com{link}",
                'shop_name': shop_name,
                'image_url': image_url,
                'is_available': is_available
            }
        except Exception as e:
            logger.debug(f"Error detallando producto: {str(e)[:50]}")
            return None

if __name__ == "__main__":
    # Test run
    async def test():
        s = TradeinnScraper()
        s.log_callback = print
        res = await s.search("masters of the universe origins")
        for r in res:
            print(f"[{r.shop_name}] {r.product_name} - {r.price}€")
    
    asyncio.run(test())
