import asyncio
import logging
import re
import io
import sys
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
    Optimized for ebay.es with routing to El Pabellón (Peer-to-Peer).
    """
    def __init__(self):
        super().__init__(shop_name="Ebay.es", base_url="https://www.ebay.es")
        self.search_url = "https://www.ebay.es/sch/i.html?_nkw="
        self.is_auction_source = True # Routes to "El Pabellón"

    async def search(self, query: str) -> List[ScrapedOffer]:
        """
        Searches ebay.es for MOTU Origins items.
        If query is 'auto', it uses the default MOTU Origins query.
        """
        search_query = "masters of the universe origins" if query == "auto" else query
        url = f"{self.search_url}{search_query.replace(' ', '+')}&_sacat=0&_sop=12" # _sop=12 for newly listed
        
        logger.info(f"🕸️ Ebay.es: Infiltrando búsqueda para '{search_query}'...")
        
        offers = []
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=self._get_random_header()["User-Agent"],
                    locale="es-ES",
                    extra_http_headers={
                        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                        "Referer": "https://www.ebay.es/",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-User": "?1",
                        "Upgrade-Insecure-Requests": "1"
                    }
                )
                page = await context.new_page()
                
                # HUMAN FLOW: Navigate to home first
                success = await self._safe_navigate(page, self.base_url)
                if not success:
                    logger.error("❌ Ebay.es: No se pudo navegar a la portada.")
                    await browser.close()
                    return []

                # Handle Cookie Banner
                try:
                    cookie_btn = await page.query_selector("#gdpr-banner-accept, #sp-cc-accept")
                    if cookie_btn:
                        await cookie_btn.click()
                        await asyncio.sleep(1)
                except:
                    pass

                # Enter Search Query
                try:
                    search_box = await page.wait_for_selector("#gh-ac")
                    await search_box.fill(search_query)
                    await search_box.press("Enter")
                    await page.wait_for_load_state("domcontentloaded")
                except Exception as e:
                    logger.error(f"❌ Ebay.es: Error en el flujo de búsqueda: {e}")
                    await browser.close()
                    return []

                # Wait for any item related class
                try:
                    await page.wait_for_selector(".s-item, .s-card", timeout=15000)
                except Exception as e:
                    logger.warning(f"⚠️ Ebay.es: No se detectaron resultados (.s-item/.s-card).")
                    await browser.close()
                    return []
                
                await asyncio.sleep(3) # Heavy lazy load wait
                
                # Extract results
                # We use a broad selector to find list items or cards
                results = await page.query_selector_all("li.s-item, .s-card, .s-item__wrapper")
                logger.info(f"📊 Ebay.es: Encontrados {len(results)} posibles resultados.")

                for res in results:
                    try:
                        # Title extraction (Multiple selectors)
                        title = None
                        for selector in [".s-item__title", ".s-card__title", "span[role='heading']", "h3"]:
                            title_el = await res.query_selector(selector)
                            if title_el:
                                title = await title_el.inner_text()
                                if title and "Shop on eBay" not in title and "anuncio" not in title.lower():
                                    break
                        
                        if not title or "Shop on eBay" in title: continue
                        # Clean noise
                        title = title.replace("Nuevo anuncio", "")
                        title = title.replace("Se abre en una nueva ventana o pestaña", "")
                        title = title.strip()

                        # Price
                        price = 0.0
                        price_el = await res.query_selector(".s-item__price, .s-card__price")
                        if price_el:
                            price_text = await price_el.inner_text()
                            price = self._normalize_price(price_text)

                        # URL
                        link_el = await res.query_selector("a.s-item__link, a.s-card__link, a")
                        if not link_el: continue
                        full_url = await link_el.get_attribute("href")
                        if not full_url or "ebay.es/itm/" not in full_url: continue
                        
                        if full_url and "?" in full_url:
                            full_url = full_url.split("?")[0]

                        # Image
                        img_el = await res.query_selector("img")
                        image_url = await img_el.get_attribute("src") if img_el else None

                        # --- PHASE 39: AUCTION INTELLIGENCE ---
                        sale_type = "Fixed_P2P"
                        bids_count = 0
                        time_left_raw = None
                        expiry_at = None

                        # Detect Auction vs Fixed
                        bid_el = await res.query_selector(".s-item__bids, .s-item__bid-count")
                        if bid_el:
                            sale_type = "Auction"
                            bid_text = await bid_el.inner_text()
                            bids_match = re.search(r'(\d+)', bid_text)
                            if bids_match:
                                bids_count = int(bids_match.group(1))
                        
                        # Detect "Compra ya" (Fixed Price)
                        purchase_options = await res.query_selector(".s-item__purchase-options")
                        if purchase_options:
                            opt_text = await purchase_options.inner_text()
                            if "Compra ya" in opt_text or "¡Cómpralo ya!" in opt_text:
                                sale_type = "Fixed_P2P"

                        # Time Left
                        time_el = await res.query_selector(".s-item__time-left, .s-item__time")
                        if time_el:
                            time_left_raw = await time_el.inner_text()
                            # Basic string cleanup
                            time_left_raw = time_left_raw.replace("¡Solo queda(n) ", "").replace("!", "").strip()
                            
                            # Simple expiration estimation (Phase 39)
                            # Logic: If string has 'd', 'h', 'm', try to add to now.
                            try:
                                from datetime import timedelta
                                now = datetime.utcnow()
                                offset = timedelta()
                                
                                # Examples: "2 d 14 h", "13 h 5 m", "58 m"
                                d_match = re.search(r'(\d+)\s*d', time_left_raw)
                                h_match = re.search(r'(\d+)\s*h', time_left_raw)
                                m_match = re.search(r'(\d+)\s*m', time_left_raw)
                                
                                if d_match: offset += timedelta(days=int(d_match.group(1)))
                                if h_match: offset += timedelta(hours=int(h_match.group(1)))
                                if m_match: offset += timedelta(minutes=int(m_match.group(1)))
                                
                                if offset.total_seconds() > 0:
                                    expiry_at = now + offset
                            except:
                                pass

                        if price > 0 and full_url not in [o.url for o in offers]:
                            offers.append(ScrapedOffer(
                                product_name=title,
                                price=price,
                                url=full_url,
                                shop_name=self.shop_name,
                                image_url=image_url,
                                ean=None,
                                source_type="Peer-to-Peer",
                                sale_type=sale_type,
                                bids_count=bids_count,
                                time_left_raw=time_left_raw,
                                expiry_at=expiry_at
                            ))
                            self.items_scraped += 1

                    except Exception as e:
                        logger.warning(f"⚠️ Error procesando resultado de Ebay: {e}")
                        continue

                await browser.close()
                
        except Exception as e:
            logger.error(f"❌ Fallo crítico en EbayScraper: {e}")
            self.errors += 1
        
        return offers
