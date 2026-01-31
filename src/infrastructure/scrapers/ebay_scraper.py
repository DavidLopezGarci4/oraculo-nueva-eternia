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
        Implementa un 'Watchdog' para evitar bloqueos infinitos.
        """
        search_query = "masters of the universe origins" if query == "auto" else query
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
        
        self._log(f"🕸️ Ebay.es: Iniciando extracción estratégica para '{search_query}'...")
        
        offers = []
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=self._get_random_header()["User-Agent"],
                    locale="es-ES",
                    timezone_id="Europe/Madrid"
                )
                page = await context.new_page()
                
                # Watchdog: Timeout total para la sesión de eBay (5 minutos p/ manual)
                try:
                    await asyncio.wait_for(self._run_search_session(page, target_url, offers), timeout=300)
                except asyncio.TimeoutError:
                    self._log("⚠️ Ebay.es: Watchdog activado - Tiempo límite de 5min excedido. Retornando resultados parciales.", level="warning")
                except Exception as e:
                    self._log(f"⚠️ Ebay.es: Error durante la sesión: {str(e)[:100]}", level="error")
                
                await browser.close()
                
        except Exception as e:
            self._log(f"❌ Error crítico en EbayScraper: {str(e)[:100]}", level="error")
            self.errors += 1
        
        return offers

    async def _run_search_session(self, page: Page, target_url: str, offers: List[ScrapedOffer]):
        """Internal worker for the watchdog-protected session."""
        # 1. Navegación inicial
        await self._safe_navigate(page, self.base_url)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # 2. Navegación a la URL de resultados
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3) 
        
        page_num = 1
        while page_num <= 3:
            self._log(f"📄 Procesando página {page_num} de Ebay.es...")
            
            # Sigilo: Scroll
            await self._stealth_scroll(page)
            
            # Extración optimizada via JS injection (Watchdog por página: 60s)
            try:
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
            next_button = await page.query_selector("a.pagination__next")
            if next_button:
                await asyncio.sleep(random.uniform(2, 4))
                await next_button.click()
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(2)
                page_num += 1
            else:
                break

    async def _stealth_scroll(self, page: Page):
        for _ in range(random.randint(3, 6)):
            await page.mouse.wheel(0, random.randint(500, 900))
            await asyncio.sleep(random.uniform(0.2, 0.5))

    async def _extract_page_items(self, page: Page) -> List[ScrapedOffer]:
        try:
            # Captura masiva vía Evaluate
            data = await page.evaluate('''() => {
                const results = [];
                const selector = "li.s-item, .s-card, .s-item__wrapper";
                const elements = document.querySelectorAll(selector);
                
                elements.forEach(el => {
                    const titleEl = el.querySelector(".s-item__title, .s-card__title, [role='heading']");
                    const priceEl = el.querySelector(".s-item__price, .s-card__price");
                    const linkEl = el.querySelector("a.s-item__link, a.s-card__link, a");
                    const imgEl = el.querySelector("img");
                    const bidEl = el.querySelector(".s-item__bids, .s-item__bid-count");
                    const timeEl = el.querySelector(".s-item__time-left, .s-item__time");
                    
                    if (titleEl && priceEl && linkEl) {
                        let title = titleEl.innerText || "";
                        // Limpieza de ruido de eBay
                        title = title.replace("Nuevo anuncio", "").replace("Se abre en una nueva ventana", "").trim();
                        if (title.toLowerCase().includes("shop on ebay")) return;

                        results.push({
                            title: title,
                            price_raw: priceEl.innerText,
                            url: linkEl.href,
                            image_url: imgEl ? imgEl.src : null,
                            bid_text: bidEl ? bidEl.innerText : null,
                            time_left_raw: timeEl ? timeEl.innerText : null
                        });
                    }
                });
                return results;
            }''')
            
            page_offers = []
            for item in data:
                try:
                    price = self._normalize_price(item['price_raw'])
                    if price <= 0: continue
                    
                    url = item['url'].split("?")[0]
                    if "ebay.es/itm/" not in url: continue
                    
                    sale_type = "Fixed_P2P"
                    bids_count = 0
                    if item['bid_text']:
                        sale_type = "Auction"
                        bids_match = re.search(r'(\d+)', item['bid_text'])
                        if bids_match: bids_count = int(bids_match.group(1))
                    
                    expiry_at = None
                    time_left = item['time_left_raw']
                    if time_left:
                        time_left = time_left.replace("¡Solo queda(n) ", "").replace("!", "").strip()
                        try:
                            from datetime import timedelta
                            now = datetime.utcnow()
                            offset = timedelta()
                            d_match = re.search(r'(\d+)\s*d', time_left)
                            h_match = re.search(r'(\d+)\s*h', time_left)
                            m_match = re.search(r'(\d+)\s*m', time_left)
                            if d_match: offset += timedelta(days=int(d_match.group(1)))
                            if h_match: offset += timedelta(hours=int(h_match.group(1)))
                            if m_match: offset += timedelta(minutes=int(m_match.group(1)))
                            if offset.total_seconds() > 0: expiry_at = now + offset
                        except: pass

                    page_offers.append(ScrapedOffer(
                        product_name=item['title'],
                        price=price,
                        url=url,
                        shop_name="Ebay.es",
                        image_url=item['image_url'],
                        source_type="Peer-to-Peer",
                        sale_type=sale_type,
                        bids_count=bids_count,
                        time_left_raw=time_left,
                        expiry_at=expiry_at,
                        first_seen_at=datetime.utcnow(),
                        is_sold=False
                    ))
                except: continue
            return page_offers
        except Exception as e:
            self._log(f"⚠️ Fallo en evaluación JS: {e}", level="warning")
            return []
