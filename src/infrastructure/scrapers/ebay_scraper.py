import asyncio
import logging
import re
import io
import sys
import random
import unicodedata
from typing import List, Optional, Dict
from datetime import datetime, timezone
from playwright.async_api import Page, BrowserContext
from src.core.vintage_utils import check_is_vintage
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
        self._session = None
        self._session_headers: Optional[Dict[str, str]] = None

    @staticmethod
    def _normalize_accents(text: str) -> str:
        """Elimina diacríticos para comparar variantes como orígenes / origenes."""
        if not text:
            return ""
        return "".join(
            ch for ch in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(ch)
        )

    @staticmethod
    def _extract_canonical_itm_url(item) -> Optional[str]:
        """Extrae la URL canónica `/itm/` de una tarjeta .s-item o .s-card evitando enlaces auxiliares y dummies."""
        anchors = item.select("a.s-item__link, a.s-card__link, a[href*='/itm/']")
        for anchor in anchors:
            href = (anchor.get("href") or "").strip()
            if not href or "/itm/" not in href:
                continue
            clean = href.split("?")[0]
            if clean.startswith("/itm/"):
                clean = f"https://www.ebay.es{clean}"
            if not ("ebay.es/itm/" in clean or "ebay.com/itm/" in clean):
                continue
            if re.search(r"/itm/(?:[^/]+/)?123456/?$", clean):
                continue
            return clean
        return None

    @staticmethod
    def _extract_itm_id(url: str) -> str:
        m = re.search(r"/itm/(?:[^/]+/)?(\d+)", url)
        return m.group(1) if m else url

    @classmethod
    def _matches_query_context(cls, title: str, search_query: str) -> bool:
        """Acepta Origins y equivalentes españoles/sublíneas MOTU Origins."""
        title_norm = cls._normalize_accents(title.lower())
        query_norm = cls._normalize_accents(search_query.lower())
        if "origins" in query_norm or "origenes" in query_norm:
            return any(
                kw in title_norm
                for kw in ("origins", "origenes", "cartoon collection", "turtles of grayskull")
            )
        return True

    async def _init_session(self):
        """Inicializa la sesión de curl-cffi con una visita a la home y cabeceras fijas por sesión."""
        from curl_cffi.requests import AsyncSession
        if self._session is None:
            self._session = AsyncSession(impersonate="chrome124")
            self._session_headers = self._get_random_header()
            try:
                self._log("🍪 [Sirius-E] Inicializando sesión (Warm-up)...")
                resp = await self._session.get(self.base_url, headers=self._session_headers, timeout=30)
                if resp.status_code in (403, 429, 503):
                    self._log(f"⚠️ [Sirius-E] Warm-up devolvió HTTP {resp.status_code}.", level="debug")
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                self._log(f"⚠️ Error en warm-up de eBay: {e}", level="warning")

    async def search(self, query: str) -> List[ScrapedOffer]:
        self.blocked = False
        if query != "auto" and check_is_vintage(query):
            self._log(f"🚫 Ebay.es: Búsqueda vintage bloqueada por política AGENTS.md ({query}).", level="warning")
            return []

        if query == "auto":
            # AGENTS.md Regla 2: consultas enfocadas estrictamente a Masters of the Universe Origins
            queries_config = [
                "masters of the universe origins",
                "masters del universo origenes"
            ]
        else:
            queries_config = [query]

        offers: List[ScrapedOffer] = []
        await self._init_session()
        try:
            return await self._search_with_active_session(queries_config, offers)
        finally:
            if self._session is not None:
                try:
                    await self._session.close()
                except Exception:
                    pass
                self._session = None

    async def _search_with_active_session(self, queries_config: List[str], offers: List[ScrapedOffer]) -> List[ScrapedOffer]:
        playwright_queries = []
        seen_itm_ids = {self._extract_itm_id(o.url) for o in offers}
        base_headers = self._session_headers or self._get_random_header()
        fast_blocked_queries = 0

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
                req_headers = {
                    **base_headers,
                    "Referer": "https://www.ebay.es/",
                    "sec-fetch-site": "same-origin",
                }
                resp = await self._session.get(target_url, headers=req_headers, timeout=30)
                if resp.status_code == 200:
                    if self._detect_block(resp.text):
                        fast_blocked_queries += 1
                    else:
                        html = resp.text
                else:
                    self._log(f"⚠️ Sirius-E: HTTP {resp.status_code} para '{search_query}'.", level="warning")
                    if resp.status_code in (403, 429, 503):
                        fast_blocked_queries += 1
            except Exception as e:
                self._log(f"⚠️ Error en búsqueda rápida Sirius-E para '{search_query}': {e}", level="warning")
            
            query_offers = []
            if html:
                query_offers = self._parse_ebay_html(html, search_query)
                
            if query_offers:
                self._log(f"✅ [Sirius-E] Capturadas {len(query_offers)} reliquias directas para '{search_query}'.")
                for o in query_offers:
                    itm_key = self._extract_itm_id(o.url)
                    if itm_key not in seen_itm_ids:
                        seen_itm_ids.add(itm_key)
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
            pw_blocked = False
            pw_had_error = False
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=base_headers["User-Agent"],
                    locale="es-ES"
                )
                page = await context.new_page()
                try:
                    for search_query, target_url in playwright_queries:
                        self._log(f"🧭 Playwright: Navegando a resultados de '{search_query}'...")
                        try:
                            resp = await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                            current_url = (page.url or "").lower()
                            html_check = await page.content()
                            resp_status = getattr(resp, "status", None) if resp else None
                            if (
                                "splashui/captcha" in current_url
                                or resp_status in (403, 429, 503)
                                or self._detect_block(html_check)
                            ):
                                self._log(
                                    f"🛡️ [Sirius-E] Bloqueo anti-bot / CAPTCHA detectado en eBay ({(page.url or target_url)[:80]}). "
                                    "Abortando escalamiento para proteger ofertas activas.",
                                    level="warning",
                                )
                                self.blocked = True
                                pw_blocked = True
                                break

                            await asyncio.sleep(3)
                            await self._stealth_scroll(page)
                            new_offers = await self._extract_page_items(page, search_query)
                            self._log(f"🔭 Playwright extrajo {len(new_offers)} items para '{search_query}'.")
                            for o in new_offers:
                                itm_key = self._extract_itm_id(o.url)
                                if itm_key not in seen_itm_ids:
                                    seen_itm_ids.add(itm_key)
                                    offers.append(o)
                                    self.items_scraped += 1
                        except Exception as e:
                            pw_had_error = True
                            self._log(f"❌ Error en Playwright para '{search_query}': {e}", level="error")
                        await asyncio.sleep(random.uniform(3.0, 5.0))
                finally:
                    await browser.close()

            if not offers and fast_blocked_queries == len(queries_config) and (pw_blocked or pw_had_error):
                self.blocked = True

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
                title_el = item.select_one(".s-item__title, .s-card__title, [role='heading']")
                if not title_el: continue
                title_raw = title_el.get_text(strip=True)
                title_raw = re.sub(r'(?i)(Nuevo anuncio|Se abre en una nueva ventana o pestaña|Se abre en una nueva ventana|o pestaña)', '', title_raw)
                title = re.sub(r'\s+', ' ', title_raw).strip()
                
                # Ignorar basura de eBay
                if not title or "shop on ebay" in title.lower(): continue

                price_el = item.select_one(".s-item__price, .s-card__price")
                price = self._normalize_price(price_el.get_text()) if price_el else 0.0
                
                if price <= 0: continue

                url = self._extract_canonical_itm_url(item)
                if not url: continue

                # Filtro Inteligente Contextual (Phase 43) & Bloqueo Vintage (AGENTS.md)
                if not self._matches_query_context(title, search_query):
                    continue
                if check_is_vintage(title):
                    continue

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
                    first_seen_at=datetime.now(timezone.utc).replace(tzinfo=None)
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
                    
                    # Limpieza táctica de títulos (accesibilidad y espacios múltiples)
                    title_clean = re.sub(r'(?i)(Nuevo anuncio|Se abre en una nueva ventana o pestaña|Se abre en una nueva ventana|o pestaña)', '', title_el.get_text(strip=True))
                    title_raw = re.sub(r'\s+', ' ', title_clean).strip()
                    title = title_raw.lower()
                    full_text = item.get_text(separator=" ", strip=True).lower()
                    
                    # Filtro Inteligente Contextual (Phase 43) & Bloqueo Vintage (AGENTS.md)
                    if not title_raw or "shop on ebay" in title:
                        continue
                    if not self._matches_query_context(title_raw, search_query):
                        continue
                    if check_is_vintage(title_raw):
                        continue
                    
                    # Filtro de seguridad para evitar "usados"
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

                    url = self._extract_canonical_itm_url(item)
                    if not url: continue
                    
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
                        first_seen_at=datetime.now(timezone.utc).replace(tzinfo=None),
                        is_sold=False
                    ))
                except Exception:
                    continue
            
            return page_offers
        except Exception as e:
            self._log(f"⚠️ Error en extracción: {e}", level="warning")
            return []
