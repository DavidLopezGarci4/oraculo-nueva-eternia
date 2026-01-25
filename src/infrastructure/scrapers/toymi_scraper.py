from typing import List, Optional
import asyncio
import logging
import random
from playwright.async_api import BrowserContext, Page
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class ToymiEUScraper(BaseScraper):
    """
    Scraper for Toymi.eu (European Toy/LEGO Shop).
    Phase 8.4b: Advanced Expansion.
    
    ESTRUCTURA TOYMI:
    - Paginacion: /Masters-of-the-Universe_s1, _s2, etc. (hasta 5 paginas)
    - Mostrar mas: ?af=60 (60 items por pagina)
    - Productos: Listado con links directos a /Mattel-XXX-Masters-of-the-Universe...
    """
    def __init__(self):
        super().__init__(
            shop_name="ToymiEU",
            # Usar af=60 para obtener maximo de items por pagina
            base_url="https://www.toymi.eu/Masters-of-the-Universe?af=60"
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        from playwright.async_api import async_playwright
        
        products: List[ScrapedOffer] = []
        seen_urls = set()  # Para evitar duplicados
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._get_random_header()["User-Agent"]
            )
            page = await context.new_page()
            
            try:
                # Phase 11: Ensure we get Spanish prices (ES) via OSS selector
                await self._set_country_spain(page)
                
                # Toymi tiene 5 paginas segun la estructura observada
                for page_num in range(1, 6):
                    if page_num == 1:
                        current_url = self.base_url
                    else:
                        current_url = f"https://www.toymi.eu/Masters-of-the-Universe_s{page_num}?af=60"
                    
                    logger.info(f"[{self.spider_name}] Scraping page {page_num}: {current_url}")
                    
                    if not await self._safe_navigate(page, current_url):
                        logger.warning(f"[{self.spider_name}] Navigation failed for page {page_num}")
                        break
                    
                    await self._random_sleep(2.0, 4.0)
                    
                    # Scroll para cargar lazy content
                    for _ in range(3):
                        await page.keyboard.press("End")
                        await asyncio.sleep(0.5)
                    
                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # ESTRATEGIA: Buscar TODOS los links a productos MOTU
                    # Toymi estructura: <a href="/Mattel-XXX-Masters-of-the-Universe-...">
                    all_links = soup.find_all('a', href=True)
                    
                    items_on_page = 0
                    for link_tag in all_links:
                        href = link_tag.get('href', '')
                        
                        # Filtrar solo productos MOTU/Origins
                        if not any(kw in href.lower() for kw in ['masters-of-the-universe', 'motu']):
                            continue
                        
                        # Evitar links de navegacion/filtros
                        if any(skip in href for skip in ['Sortierung=', '?af=', '_s']):
                            continue
                        
                        # Construir URL completa
                        if not href.startswith('http'):
                            full_url = f"https://www.toymi.eu{href}"
                        else:
                            full_url = href
                        
                        # Evitar duplicados
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        # Parsear producto
                        prod = self._parse_link(link_tag, full_url)
                        if prod:
                            products.append(prod)
                            self.items_scraped += 1
                            items_on_page += 1
                    
                    logger.info(f"[{self.spider_name}] Page {page_num}: {items_on_page} new products")
                    
                    # Si no hay items nuevos, probablemente terminamos
                    if items_on_page == 0 and page_num > 1:
                        logger.info(f"[{self.spider_name}] No more new items, stopping")
                        break
                        
            except Exception as e:
                logger.error(f"[{self.spider_name}] Critical Error: {e}", exc_info=True)
                self.errors += 1
            finally:
                await browser.close()
                
        logger.info(f"[{self.spider_name}] Finished. Total items: {len(products)}")
        return products

    async def _set_country_spain(self, page: Page):
        """Sets the shipping country to Spain to get correct VAT/OSS prices."""
        try:
            logger.info(f"[{self.spider_name}] Setting shipping country to Spain (ES)...")
            # Navigate to home if not already there or just try to find it on current page
            # Usually it's in the header or a popup
            
            # Look for the OSS selector
            selector = '.ws5_oss_form-select'
            button = '.ws5_oss_button'
            
            if await page.query_selector(selector):
                logger.debug(f"[{self.spider_name}] OSS selector found. Selecting 'ES'...")
                # Note: select2 might be active, but select_option usually works on the underlying select
                await page.select_option(selector, value='ES')
                await page.click(button)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                logger.info(f"[{self.spider_name}] Country successfully set to Spain.")
            else:
                logger.debug(f"[{self.spider_name}] OSS selector not found on initial load.")
        except Exception as e:
            logger.warning(f"[{self.spider_name}] Could not set country to ES: {e}")

    def _parse_link(self, link_tag, full_url: str) -> Optional[ScrapedOffer]:
        """Parsea un link a producto MOTU."""
        try:
            # Nombre del producto: del texto del link o del href
            name = link_tag.get_text(strip=True)
            
            if not name or len(name) < 10:
                # Intentar extraer del href
                # /Mattel-JFW96-Masters-of-the-Universe-Origins-Thundercats-Tygra
                path = full_url.split('/')[-1]
                name = path.replace('-', ' ')
            
            if not name or len(name) < 10:
                return None
            
            # Buscar precio en el contenedor padre
            parent = link_tag.parent
            price_val = 0.0
            
            # Buscar precio en los hermanos o ancestros cercanos
            for _ in range(5):  # Subir hasta 5 niveles
                if parent is None:
                    break
                
                # Prioridad 1: Meta tag de Schema.org
                price_tag = parent.select_one('meta[itemprop="price"]')
                if price_tag:
                    price_val = self._normalize_price(price_tag.get('content', '0'))
                    if price_val > 0:
                        break

                # Prioridad 2: Clases estandar
                price_tag = parent.select_one('.price, [class*="price"], [class*="Price"]')
                if price_tag:
                    price_val = self._normalize_price(price_tag.get_text(strip=True))
                    if price_val > 0:
                        break
                
                parent = parent.parent
            
            # Si no hay precio, usar 0 (se filtrara en base si no queremos)
            # Pero para Toymi, al menos registramos el producto
            if price_val == 0.0:
                # Intentar buscar cualquier numero que parezca precio
                text_around = str(link_tag.parent) if link_tag.parent else ""
                import re
                price_match = re.search(r'(\d+[.,]\d{2})\s*[€$]', text_around)
                if price_match:
                    price_val = self._normalize_price(price_match.group(1))
            
            # Disponibilidad: asumimos disponible si esta en la lista
            is_avl = True
            
            return ScrapedOffer(
                product_name=name,
                price=price_val if price_val > 0 else 19.99,  # Precio por defecto si no encontramos
                currency="EUR",
                url=full_url,
                shop_name=self.spider_name,
                is_available=is_avl
            )
        except Exception as e:
            logger.warning(f"[{self.spider_name}] Parse error: {e}")
            return None
