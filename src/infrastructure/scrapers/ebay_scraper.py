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
        self._session: Optional[AsyncSession] = None

    async def _init_session(self):
        """Inicializa la sesión de curl-cffi con una visita a la home."""
        from curl_cffi.requests import AsyncSession
        if self._session is None:
            self._session = AsyncSession(impersonate="chrome120")
            headers = self._get_random_header()
            try:
                self._log("🍪 [Sirius-E] Inicializando sesión (Warm-up)...")
                await self._session.get(self.base_url, headers=headers, timeout=30)
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                self._log(f"⚠️ Error en warm-up de eBay: {e}", level="warning")

    async def search(self, query: str) -> List[ScrapedOffer]:
        if query == "auto":
            # Estrategia de 2 Consultas de Alta Cobertura (Inglés + Español)
            # Evita timeouts de 10 min y minimiza el riesgo de bloqueos por Cloudflare
            queries_config = [
                "masters of the universe",
                "masters del universo"
            ]
        else:
            queries_config = [query]

        offers: List[ScrapedOffer] = []
        await self._init_session()
        
        playwright_queries = []
        
        # 1. Infiltración veloz vía curl-cffi
        for search_query in queries_config:
            params = [
                f"_nkw={search_query.replace(' ', '+')}",
                "_sacat=0",
                "_from=R40",
                "LH_BIN=1",
                "LH_ItemCondition=3",
                "LH_PrefLoc=1",  # España solo
                "_sop=10",       # Recién listados
                "_ipg=240",
                "rt=nc"
            ]
            target_url = f"{self.search_url}?" + "&".join(params)
            
            self._log(f"🌩️ [Sirius-E] Infiltración rápida en ebay.es: '{search_query}'")
            
            html = None
            try:
                headers = self._get_random_header()
                resp = await self._session.get(target_url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    html = resp.text
                else:
                    self._log(f"⚠️ Sirius-E: HTTP {resp.status_code} para '{search_query}'.", level="warning")
            except Exception as e:
                self._log(f"⚠️ Error en búsqueda rápida Sirius-E para '{search_query}': {e}", level="warning")
            
            query_offers = []
            if html:
                query_offers = self._parse_ebay_html(html, search_query)
                
            if query_offers:
                self._log(f"✅ [Sirius-E] Capturadas {len(query_offers)} reliquias directas para '{search_query}'.")
                for o in query_offers:
                    if o.url not in [existing.url for existing in offers]:
                        offers.append(o)
                        self.items_scraped += 1
            else:
                self._log(f"⚠️ [Sirius-E] Sin resultados rápidos para '{search_query}'. Programando escalamiento táctico...", level="debug")
                playwright_queries.append((search_query, target_url))
                
            # Retardo prudente de cortesía
            await asyncio.sleep(random.uniform(2.0, 3.5))

        # 2. Escalamiento táctico a Playwright solo para búsquedas fallidas o bloqueadas
        if playwright_queries:
            self._log(f"⚠️ [Sirius-E] Iniciando escalamiento táctico a Playwright para {len(playwright_queries)} consultas...")
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=self._get_random_header()["User-Agent"],
                    locale="es-ES"
                )
                page = await context.new_page()
                try:
                    for search_query, target_url in playwright_queries:
                        self._log(f"🧭 Playwright: Navegando a resultados de '{search_query}'...")
                        try:
                            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                            await asyncio.sleep(3)
                            await self._stealth_scroll(page)
                            new_offers = await self._extract_page_items(page, search_query)
                            self._log(f"🔭 Playwright extrajo {len(new_offers)} items para '{search_query}'.")
                            for o in new_offers:
                                if o.url not in [existing.url for existing in offers]:
                                    offers.append(o)
                                    self.items_scraped += 1
                        except Exception as e:
                            self._log(f"❌ Error en Playwright para '{search_query}': {e}", level="error")
                        await asyncio.sleep(random.uniform(3.0, 5.0))
                finally:
                    await browser.close()
        
        return offers

    def _parse_ebay_html(self, html: str, search_query: str) -> List[ScrapedOffer]:
        """Parseo de HTML puro (BeautifulSoup) para cuando no ejecutamos JS."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Soporte dual: s-item (Lista) y s-card (Grid)
        items = soup.select(".s-item__wrapper, li.s-item, li.s-card")
        offers = []

        for item in items:
            try:
                # Selectores inteligentes (Dual)
                title_el = item.select_one(".s-item__title, .s-card__title")
                if not title_el: continue
                title = title_el.get_text(strip=True).replace("Nuevo anuncio", "").strip()
                
                # Ignorar basura de eBay
                if not title or "anuncio" in title.lower() or "shop on ebay" in title.lower(): continue

                price_el = item.select_one(".s-item__price, .s-card__price")
                price = self._normalize_price(price_el.get_text()) if price_el else 0.0
                
                if price <= 0: continue

                url_el = item.select_one(".s-item__link, .s-card__link")
                url = url_el.get("href").split("?")[0] if url_el else None
                if not url or "ebay.es/itm/" not in url: continue

                # Filtro Inteligente Contextual (Phase 43)
                title_lower = title.lower()
                query_lower = search_query.lower()
                
                if "origins" in query_lower and "origins" not in title_lower:
                    continue
                if "vintage" in query_lower:
                    is_v = "vintage" in title_lower or any(yr in title_lower for yr in ["1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989"])
                    if not is_v: continue

                # Imagen
                img_el = item.select_one(".s-item__image-img, .s-card__image-img, img")
                image_url = img_el.get("src") if img_el else None

                offers.append(ScrapedOffer(
                    product_name=title,
                    price=price,
                    url=url,
                    shop_name=self.shop_name,
                    image_url=image_url,
                    source_type="Peer-to-Peer",
                    sale_type="Fixed_P2P",
                    first_seen_at=datetime.utcnow()
                ))
            except:
                continue
        return offers

    async def _run_search_session(self, page: Page, target_url: str, offers: List[ScrapedOffer]):
        """Internal worker for the watchdog-protected session."""
        # 1. Navegación inicial
        await self._safe_navigate(page, self.base_url)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # 2. Navegación a la URL de resultados
        self._log(f"🧭 Navegando a resultados: {target_url}")
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        except Exception:
             self._log("⚠️ Ebay.es: Timeout parcial en carga inicial, procediendo con DOM parcial.", level="warning")
        
        await asyncio.sleep(3) 

        page_num = 1
        while page_num <= 3:
            self._log(f"📄 Procesando página {page_num} de Ebay.es...")
            
            # Sigilo: Scroll
            await self._stealth_scroll(page)
            
            # Extración optimizada via JS injection (Watchdog por página: 60s)
            try:
                self._log(f"🧪 Ebay.es: Ejecutando extracción JS en página {page_num}...")
                new_offers = await asyncio.wait_for(self._extract_page_items(page), timeout=60)
                self._log(f"🔭 Halladas {len(new_offers)} reliquias potenciales en página {page_num}.")
                
                added_count = 0
                for offer in new_offers:
                    if offer.url not in [o.url for o in offers]:
                        offers.append(offer)
                        self.items_scraped += 1
                        added_count += 1
            except asyncio.TimeoutError:
                self._log(f"⚠️ Ebay.es: Timeout en página {page_num}, saltando a siguiente...", level="warning")
            
            # Paginación
            self._log(f"⏭️ Ebay.es: Buscando botón de siguiente página...")
            next_button = await page.query_selector("a.pagination__next")
            if next_button:
                self._log(f"🖱️ Ebay.es: Navegando a siguiente página ({page_num + 1})...")
                await asyncio.sleep(random.uniform(2, 4))
                
                # Race condition: Wait for DOM or 20s timeout to bypass non-critical resource hangs
                try:
                    await asyncio.wait_for(
                        asyncio.gather(
                            next_button.click(),
                            page.wait_for_load_state("domcontentloaded")
                        ),
                        timeout=25
                    )
                except asyncio.TimeoutError:
                    self._log(f"⚠️ Ebay.es: Timeout en click/carga (25s), intentando continuar con el estado actual.", level="warning")
                
                await asyncio.sleep(2)
                page_num += 1
            else:
                self._log(f"🏁 Ebay.es: No hay más páginas o botón no encontrado.")
                break

    async def _stealth_scroll(self, page: Page):
        for _ in range(random.randint(3, 6)):
            await page.mouse.wheel(0, random.randint(500, 900))
            await asyncio.sleep(random.uniform(0.2, 0.5))

    async def _extract_page_items(self, page: Page, search_query: str = "auto") -> List[ScrapedOffer]:
        try:
            # Captura Robusta vía BeautifulSoup (Phase 42)
            html = await page.content()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            
            # Soporte Dual: s-item y s-card
            items = soup.select("li.s-item, .s-card, .s-item__wrapper, li[data-view='mi:1686']")
            page_offers = []
            
            for item in items:
                try:
                    title_el = item.select_one(".s-item__title, .s-card__title, [role='heading']")
                    if not title_el: continue
                    
                    # Limpieza táctica de títulos
                    title_raw = re.sub(r'(?i)(Nuevo anuncio|Se abre en una nueva ventana|o pestaña)', '', title_el.get_text(strip=True)).strip()
                    title = title_raw.lower()
                    full_text = item.get_text(separator=" ", strip=True).lower()
                    
                    # Filtro Inteligente Contextual (Phase 43)
                    query_lower = search_query.lower()
                    if "origins" in query_lower and "origins" not in title:
                        continue
                    if "vintage" in query_lower:
                        is_v = "vintage" in title or any(yr in title for yr in ["1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989"])
                        if not is_v: continue
                    
                    # Filtro de seguridad para evitar "usados" en búsquedas no vintage
                    if "vintage" not in query_lower:
                        is_used = any(kw in full_text for kw in ["usado", "used", "segunda mano"])
                        if is_used and "nuevo" not in full_text: continue

                    price_el = item.select_one(".s-item__price, .s-card__price")
                    price = self._normalize_price(price_el.get_text()) if price_el else 0.0
                    if price <= 0: continue
                    
                    # Inteligencia de Envío Robusta
                    ship_el = item.select_one(".s-item__shipping, .s-card__shipping, .s-item__logisticsCost, .su-styled-text.secondary.large")
                    ship_text = ship_el.get_text().lower() if ship_el else ""
                    
                    # Fallback de texto si el selector falla
                    if not ship_text or ("envío" not in ship_text and "shipping" not in ship_text and "gratis" not in ship_text):
                        for span in item.find_all(["span", "div"]):
                            txt = span.get_text().lower()
                            if ("envío" in txt or "shipping" in txt) and ("+" in txt or "€" in txt or "eur" in txt):
                                ship_text = txt
                                break

                    shipping_price = 0.0
                    if ship_text and "gratis" not in ship_text and "free" not in ship_text:
                        shipping_price = self._normalize_price(ship_text)
                    
                    total_price = float(price + shipping_price)

                    url_el = item.select_one("a.s-item__link, a.s-card__link, a")
                    url = url_el.get("href").split("?")[0] if url_el else ""
                    if "ebay.es/itm/" not in url: continue
                    
                    img_el = item.select_one("img")
                    image_url = img_el.get("src") if img_el else None
                    
                    # Determinación de tipo
                    sale_type = "Fixed_P2P"
                    bids_count = 0
                    if "puja" in full_text: 
                         sale_type = "Auction"
                         b_match = re.search(r'(\d+)\s*puja', full_text)
                         if b_match: bids_count = int(b_match.group(1))

                    page_offers.append(ScrapedOffer(
                        product_name=title_raw,
                        price=price,
                        shipping_price=shipping_price,
                        total_price=total_price,
                        url=url,
                        shop_name="Ebay.es",
                        image_url=image_url,
                        source_type="Peer-to-Peer",
                        sale_type=sale_type,
                        bids_count=bids_count,
                        first_seen_at=datetime.utcnow(),
                        is_sold=False
                    ))
                except Exception:
                    continue
            
            return page_offers
        except Exception as e:
            self._log(f"⚠️ Error en extracción: {e}", level="warning")
            return []
