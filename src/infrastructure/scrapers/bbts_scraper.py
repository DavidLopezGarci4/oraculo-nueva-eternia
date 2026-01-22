from typing import List, Optional
import asyncio
import logging
import random
import re
from playwright.async_api import BrowserContext, Page
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class BigBadToyStoreScraper(BaseScraper):
    """
    Scraper for BigBadToyStore.com (USA - Major International Action Figures Retailer).
    Phase 8.4b: Advanced Expansion.
    
    OPTIMIZADO PARA GITHUB ACTIONS:
    - Stealth mode con fingerprint spoofing
    - Headers dinamicos anti-Cloudflare
    - Delays aleatorios humanizados
    - Multiples User-Agents rotativos
    """
    
    # Pool de User-Agents reales de Chrome en diferentes plataformas
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]
    
    def __init__(self):
        super().__init__(
            shop_name="BigBadToyStore",
            # Filtros precisos para MOTU Origins obtenidos del analisis del sitio
            base_url="https://www.bigbadtoystore.com/Search?HideInStock=false&HidePreorder=true&HideSoldOut=true&InventoryStatus=i&PageSize=100&SortOrder=PriceLowToHigh&Brand=2603&Series=22776"
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        from playwright.async_api import async_playwright
        
        products: List[ScrapedOffer] = []
        user_agent = random.choice(self.USER_AGENTS)
        
        async with async_playwright() as p:
            # STEALTH: Configuracion optimizada para GitHub Actions
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    # Anti-detection flags
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    # Performance en GitHub Actions (runners Linux)
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    # Fingerprint evasion
                    '--window-size=1920,1080',
                    '--start-maximized',
                ]
            )
            
            # Contexto con fingerprint realista
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1920, 'height': 1080},
                screen={'width': 1920, 'height': 1080},
                java_script_enabled=True,
                locale='en-US',
                timezone_id='America/New_York',  # BBTS es de USA
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # NYC
                permissions=['geolocation'],
                color_scheme='light',
                has_touch=False,
                is_mobile=False,
            )
            
            # Headers dinamicos anti-Cloudflare
            await context.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
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
            
            # STEALTH: Inyectar scripts anti-deteccion antes de navegar
            await page.add_init_script("""
                // Ocultar webdriver
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                
                // Falsear plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Ocultar automation flags
                window.chrome = { runtime: {} };
                
                // Falsear permisos
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)
            
            try:
                logger.info(f"[{self.spider_name}] Navegando a BBTS con stealth mode (UA: {user_agent[:50]}...)")
                
                # === PAGINACIÓN MEJORADA ===
                # BBTS usa PageIndex para la paginación (1-indexed)
                page_num = 1
                consecutive_empty_pages = 0
                has_next_page = True
                
                # Context Management for Rotation
                current_context = context
                current_page = page

                while page_num <= self.max_pages and has_next_page:
                    # Construir URL con PageIndex
                    current_url = f"{self.base_url}&PageIndex={page_num}"
                    logger.info(f"[{self.spider_name}] Scraping página {page_num}: {current_url}")
                    
                    # Delay inicial aleatorio largo (simular humano)
                    if page_num == 1:
                        await asyncio.sleep(random.uniform(2, 4))
                    else:
                        # Delay más largo entre páginas (8-15 segundos)
                        delay = random.uniform(8, 15)
                        logger.info(f"[{self.spider_name}] Esperando {delay:.1f}s antes de la siguiente página...")
                        await asyncio.sleep(delay)
                    
                    # Navigation with block detection
                    nav_success = False
                    for attempt in range(2): # Local retry with potential context refresh
                        if await self._safe_navigate(current_page, current_url, timeout=90000):
                            # Check if blocked
                            content = await current_page.content()
                            if "blocked" in content.lower() or "sorry, you have been blocked" in content.lower():
                                logger.warning(f"[{self.spider_name}] 🚫 Block detected on page {page_num}. Attempting context refresh...")
                                # Refresh context
                                await current_page.close()
                                await current_context.close()
                                
                                user_agent = random.choice(self.USER_AGENTS)
                                current_context = await browser.new_context(user_agent=user_agent)
                                current_page = await current_context.new_page()
                                await asyncio.sleep(random.uniform(5, 10))
                                continue # Retry navigation with new context
                            
                            nav_success = True
                            break
                        else:
                            logger.warning(f"[{self.spider_name}] Navigation failed for page {page_num}, attempt {attempt+1}")
                    
                    if not nav_success:
                        logger.error(f"[{self.spider_name}] Fallo definitivo al cargar BBTS página {page_num}")
                        self.blocked = True
                        break
                    
                    # Esperar renderizado JavaScript con timeout generoso
                    await current_page.wait_for_timeout(random.randint(5000, 8000))
                    
                    # Scroll humanizado para cargar lazy content
                    for i in range(3):
                        await current_page.keyboard.press("End")
                        await asyncio.sleep(random.uniform(0.8, 1.5))
                        
                        # Movimiento de mouse aleatorio (simular usuario real)
                        x = random.randint(100, 1800)
                        y = random.randint(100, 900)
                        await current_page.mouse.move(x, y)
                    
                    html_content = await current_page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Selectores multiples para BBTS (la estructura puede variar)
                    selectors = [
                        '.search-item',
                        '.product-card', 
                        '.item-card',
                        '[class*="SearchResult"]',
                        '[class*="ProductPod"]',
                        '.pod',
                        'a[href*="/Product/"]',
                    ]
                    
                    items = []
                    for selector in selectors:
                        found = soup.select(selector)
                        if found:
                            items.extend(found)
                            if page_num == 1:
                                logger.info(f"[{self.spider_name}] Selector '{selector}' encontro {len(found)} elementos")
                    
                    # Deduplicar por href (dentro de esta página)
                    seen_urls_page = set()
                    unique_items_page = []
                    for item in items:
                        href = item.get('href') or (item.select_one('a') and item.select_one('a').get('href'))
                        if href and href not in seen_urls_page:
                            seen_urls_page.add(href)
                            unique_items_page.append(item)
                    
                    logger.info(f"[{self.spider_name}] Página {page_num}: {len(unique_items_page)} items únicos")
                    
                    # Verificación de "Siguiente Página" en el DOM
                    # Buscamos <a rel="next"> o <a aria-label="Next"> o el símbolo »
                    next_link = (
                        soup.select_one('a[rel="next"]') or 
                        soup.select_one('a[aria-label="Next"]') or
                        soup.find('a', string=re.compile(r'Next|»'))
                    )
                    if not next_link:
                        # Fallback: Verificar si existe el link a la siguiente página numérica
                        next_page_url_part = f"PageIndex={page_num + 1}"
                        if not any(next_page_url_part in str(a.get('href')) for a in soup.find_all('a', href=True)):
                            logger.info(f"[{self.spider_name}] No se detectó botón 'Siguiente' ni link a pág {page_num+1}. Fin.")
                            has_next_page = False
                    
                    # Si no hay items, hemos llegado al final
                    if len(unique_items_page) == 0:
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= 2:
                            logger.info(f"[{self.spider_name}] Fin de resultados (2 páginas vacías consecutivas)")
                            has_next_page = False
                            break
                    else:
                        consecutive_empty_pages = 0
                    
                    # Parsear items de esta página
                    for item in unique_items_page:
                        prod = self._parse_item(item)
                        if prod:
                            # Evitar duplicados globales
                            if not any(p.url == prod.url for p in products):
                                products.append(prod)
                                self.items_scraped += 1
                    
                    page_num += 1
                        
            except Exception as e:
                logger.error(f"[{self.spider_name}] Error critico: {e}", exc_info=True)
                self.errors += 1
            finally:
                await browser.close()
                
        logger.info(f"[{self.spider_name}] Completado. Total: {len(products)} productos")
        return products


    def _parse_item(self, item) -> Optional[ScrapedOffer]:
        try:
            # Buscar link al producto
            a_tag = item if item.name == 'a' and item.get('href') else None
            if not a_tag:
                a_tag = item.select_one('a[href*="/Product/"]') or item.select_one('a[href]')
            if not a_tag:
                return None
            
            link = a_tag.get('href')
            if not link:
                return None
            if not link.startswith('http'):
                link = f"https://www.bigbadtoystore.com{link}"
            
            # Nombre del producto
            title_selectors = ['.product-name', '.item-name', '.title', '.pod-title', 'h2', 'h3', '[class*="Name"]', '[class*="Title"]']
            name = None
            for sel in title_selectors:
                title_tag = item.select_one(sel)
                if title_tag:
                    name = title_tag.get_text(strip=True)
                    break
            
            if not name:
                name = a_tag.get('title', '') or a_tag.get_text(strip=True)
            
            if not name or len(name) < 5:
                return None

            # Validar que el nombre contenga MOTU (ya que el link es un VariationID genérico)
            name_lower = name.lower()
            keywords = ['origin', 'master', 'motu', 'eternia', 'he-man', 'skeletor', 'mattel']
            if not any(kw in name_lower for kw in keywords):
                logger.debug(f"[{self.spider_name}] Skipping item (no keywords in name): {name}")
                return None
            
            # Precio (USD -> EUR conversion)
            price_selectors = ['.product-card-price', '.product-price', '.item-price', '.price', '.pod-price', '[class*="price"]', '[class*="Price"]']
            price_val = 0.0
            for sel in price_selectors:
                price_tag = item.select_one(sel)
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    usd_price = self._normalize_price(price_text)
                    if usd_price > 0:
                        # Conversion USD a EUR (rate aproximado)
                        price_val = round(usd_price * 0.92, 2)
                        break
            
            if price_val == 0.0:
                logger.debug(f"[{self.spider_name}] Skipping item (price is 0): {name}")
                return None
            
            # Disponibilidad
            is_avl = True
            unavailable_indicators = ['.out-of-stock', '.sold-out', '[class*="OutOfStock"]', '[class*="Unavailable"]']
            for ind in unavailable_indicators:
                if item.select_one(ind):
                    is_avl = False
                    break
            
            # Pre-orders se consideran disponibles
            if item.select_one('[class*="PreOrder"]') or 'pre-order' in str(item).lower():
                is_avl = True
            
            return ScrapedOffer(
                product_name=name,
                price=price_val,
                currency="EUR",
                url=link,
                shop_name=self.spider_name,
                is_available=is_avl
            )
        except Exception as e:
            logger.warning(f"[{self.spider_name}] Error parseando item: {e}")
            return None
