import asyncio
import logging
import re
import io
import sys
import random
from typing import List, Optional
from datetime import datetime
from playwright.async_api import Page, BrowserContext
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

# Force UTF-8 for console output to handle emojis safely
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

logger = logging.getLogger(__name__)

class EbayScraper(BaseScraper):
    """
    eBay Spain Scraper for Masters of the Universe: Origins.
    Optimized for massive extraction with pagination and stealth techniques.
    """
    def __init__(self):
        super().__init__(shop_name="Ebay.es", base_url="https://www.ebay.es")
        self.search_url = "https://www.ebay.es/sch/i.html"
        self.items_scraped = 0
        self.is_auction_source = True # Routes to "El Pabellón"

    async def search(self, query: str) -> List[ScrapedOffer]:
        """
        Infiltración masiva en ebay.es con paginación y técnicas de sigilo.
        Explora hasta 3 páginas de 240 items cada una.
        """
        search_query = "masters of the universe origins" if query == "auto" else query
        # PARÁMETROS OPTIMIZADOS (Phase 6): 
        # _ipg=240 (Máxima densidad)
        # LH_BIN=1 (Solo "¡Cómpralo ya!")
        # LH_ItemCondition=3 (Solo "Nuevo")
        # LH_PrefLoc=1 (Solo España)
        # _sop=7 (Distancia: más cercanos primero)
        params = [
            f"_nkw={search_query.replace(' ', '+')}",
            "_sacat=0",
            "_ipg=240",
            "LH_BIN=1",
            "LH_ItemCondition=3",
            "LH_PrefLoc=1",
            "_sop=7"
        ]
        target_url = f"{self.search_url}?" + "&".join(params)
        
        logger.info(f"🕸️ Ebay.es: Iniciando extracción optimizada (España, Nuevo, BIN) para '{search_query}'...")
        
        offers = []
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Sigilo Nivel 3: Contexto localizado y headers aleatorios
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=self._get_random_header()["User-Agent"],
                    locale="es-ES",
                    timezone_id="Europe/Madrid"
                )
                page = await context.new_page()
                
                # 1. Calentar sesión (Navegación inicial)
                await self._safe_navigate(page, self.base_url)
                await asyncio.sleep(random.uniform(1.0, 2.5))

                # 2. Navegación a la URL de resultados maestros
                await page.goto(target_url, wait_until="networkidle")
                
                page_num = 1
                while page_num <= 3: # Suficiente para cubrir el mercado MOTU de hoy
                    logger.info(f"📄 Procesando página {page_num} de Ebay.es...")
                    
                    # Sigilo: Scroll irregular
                    await self._stealth_scroll(page)
                    
                    # Extracción con Inteligencia de Subasta (Phase 39)
                    new_offers = await self._extract_page_items(page)
                    
                    # Deduplicación y conteo
                    added_count = 0
                    for offer in new_offers:
                        if offer.url not in [o.url for o in offers]:
                            offers.append(offer)
                            self.items_scraped += 1
                            added_count += 1
                    
                    logger.info(f"✨ Página {page_num}: {added_count} nuevas reliquias asimiladas.")

                    # 3. Lógica de Paginación Humana
                    next_button = await page.query_selector("a.pagination__next")
                    if next_button:
                        await asyncio.sleep(random.uniform(2, 5))
                        await next_button.click()
                        await page.wait_for_load_state("networkidle")
                        page_num += 1
                    else:
                        break

                await browser.close()
                
        except Exception as e:
            logger.error(f"❌ Error crítico en EbayScraper: {e}")
            self.errors += 1
        
        return offers

    async def _stealth_scroll(self, page: Page):
        """Scroll irregular que imita a un humano leyendo para evitar detección"""
        for _ in range(random.randint(4, 8)):
            await page.mouse.wheel(0, random.randint(600, 1100))
            await asyncio.sleep(random.uniform(0.3, 0.7))

    async def _extract_page_items(self, page: Page) -> List[ScrapedOffer]:
        """
        Analizador de grilla de eBay. 
        Detecta Subasta, Compra Ya, Tiempos restantes y Bids.
        """
        results = await page.query_selector_all("li.s-item, .s-card, .s-item__wrapper")
        page_offers = []
        
        for res in results:
            try:
                # 1. Título y Limpieza (Filtro de Ruido)
                title = None
                for selector in [".s-item__title", ".s-card__title", "span[role='heading']", "h3"]:
                    title_el = await res.query_selector(selector)
                    if title_el:
                        title = await title_el.inner_text()
                        if title and "Shop on eBay" not in title and "anuncio" not in title.lower():
                            break
                if not title: continue
                title = title.replace("Nuevo anuncio", "").replace("Se abre en una nueva ventana", "").strip()

                # 2. Precio Normalizado
                price = 0.0
                price_el = await res.query_selector(".s-item__price, .s-card__price")
                if price_el:
                    price_text = await price_el.inner_text()
                    price = self._normalize_price(price_text)

                # 3. URL Limpia (Sin trackings)
                link_el = await res.query_selector("a.s-item__link, a.s-card__link, a")
                if not link_el: continue
                url = await link_el.get_attribute("href")
                if not url or "ebay.es/itm/" not in url: continue
                url = url.split("?")[0]

                # 4. Imagen
                img_el = await res.query_selector("img")
                image_url = await img_el.get_attribute("src") if img_el else None

                # 5. INTELIGENCIA DE SUBASTA 3OX
                sale_type = "Fixed_P2P"
                bids_count = 0
                time_left_raw = None
                expiry_at = None

                # Detección de Puja
                bid_el = await res.query_selector(".s-item__bids, .s-item__bid-count")
                if bid_el:
                    sale_type = "Auction"
                    bid_text = await bid_el.inner_text()
                    bids_match = re.search(r'(\d+)', bid_text)
                    if bids_match: bids_count = int(bids_match.group(1))
                
                # Tiempo Final (Estimación táctica)
                time_el = await res.query_selector(".s-item__time-left, .s-item__time")
                if time_el:
                    time_left_raw = await time_el.inner_text()
                    time_left_raw = time_left_raw.replace("¡Solo queda(n) ", "").replace("!", "").strip()
                    
                    try:
                        from datetime import timedelta
                        now = datetime.utcnow()
                        offset = timedelta()
                        d_match = re.search(r'(\d+)\s*d', time_left_raw)
                        h_match = re.search(r'(\d+)\s*h', time_left_raw)
                        m_match = re.search(r'(\d+)\s*m', time_left_raw)
                        if d_match: offset += timedelta(days=int(d_match.group(1)))
                        if h_match: offset += timedelta(hours=int(h_match.group(1)))
                        if m_match: offset += timedelta(minutes=int(m_match.group(1)))
                        if offset.total_seconds() > 0: expiry_at = now + offset
                    except: pass

                if price > 0:
                    page_offers.append(ScrapedOffer(
                        product_name=title,
                        price=price,
                        url=url,
                        shop_name="Ebay.es",
                        image_url=image_url,
                        source_type="Peer-to-Peer",
                        sale_type=sale_type,
                        bids_count=bids_count,
                        time_left_raw=time_left_raw,
                        expiry_at=expiry_at,
                        first_seen_at=datetime.utcnow(),
                        is_sold=False
                    ))
            except:
                continue
        return page_offers
