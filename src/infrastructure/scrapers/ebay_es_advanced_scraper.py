import asyncio
import logging
import re
import random
from typing import List, Optional
from datetime import datetime
from playwright.async_api import Page, async_playwright
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class EbayESAdvancedScraper(BaseScraper):
    """
    eBay Spain "Black Oracle" - Scraper de Alto Rendimiento.
    Arquitectura de Doble Spider con alcance Europeo (EU Reach).
    Optimizado según 'Estrategias Avanzadas de webscraping.md'.
    """
    def __init__(self):
        super().__init__(shop_name="Ebay.es PRO", base_url="https://www.ebay.es")
        self.search_url = "https://www.ebay.es/sch/i.html"
        self.is_auction_source = True # Enviar al Pabellón automáticamente
        
    async def search(self, query: str) -> List[ScrapedOffer]:
        """
        Estrategia 'Sirius-E Advanced': 
        Infiltración dual para mercados UE con curl-cffi + Playwright fallback.
        """
        search_query = "masters of the universe origins" if query == "auto" else query
        
        # Filtros calibrados con la URL del usuario
        params = [
            f"_nkw={search_query.replace(' ', '+')}",
            "_sacat=0",
            "_from=R40",
            "LH_BIN=1",
            "LH_ItemCondition=3",
            "LH_PrefLoc=1", # España
            "_sop=10", # Recién listados
            "_ipg=240",
            "rt=nc"
        ]
        target_url = f"{self.search_url}?" + "&".join(params)
        
        self._log(f"🔎 [Sirius-E Advanced] Infiltración calibrada para: {search_query}")
        
        # 1. Infiltración Rápida (Avanzada)
        html = await self._curl_get(target_url, impersonate="chrome120")
        if html:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            # Soporte dual: s-item (Lista) y s-card (Grid) + Shipping
            items = soup.select(".s-item__wrapper, li.s-item, li.s-card")
            offers = []
            
            for item in items:
                try:
                    title_el = item.select_one(".s-item__title, .s-card__title")
                    if not title_el: continue
                    # Limpieza táctica de títulos
                    title_raw = re.sub(r'(?i)(Nuevo anuncio|Se abre en una nueva ventana|o pestaña)', '', title_el.get_text(strip=True)).strip()
                    title = title_raw.lower()
                    
                    if "origins" not in title: continue

                    url_el = item.select_one(".s-item__link, .s-card__link")
                    url = url_el.get("href").split("?")[0] if url_el else None
                    if not url or "ebay" not in url: continue

                    price_el = item.select_one(".s-item__price, .s-card__price")
                    price = self._normalize_price(price_el.get_text()) if price_el else 0.0
                    
                    if price <= 0: continue

                    # Filtro de Calidad (Menos restrictivo al ser España y haber pasado filtros en URL)
                    full_text = item.get_text().lower()
                    is_used = any(x in full_text for x in ["usado", "used", "segunda mano"])
                    if is_used and "nuevo" not in full_text: continue

                    # Inteligencia de Envío (Phase 42 - Robust)
                    ship_el = item.select_one(".s-item__shipping, .s-card__shipping, .s-item__logisticsCost, .su-styled-text.secondary.large")
                    ship_text = ship_el.get_text(separator=" ", strip=True).lower() if ship_el else ""
                    
                    if not ship_text or ("envío" not in ship_text and "shipping" not in ship_text and "gratis" not in ship_text):
                        for span in item.find_all("span"):
                            txt = span.get_text().lower()
                            if "envío" in txt or "shipping" in txt:
                                ship_text = txt
                                break

                    shipping_price = 0.0
                    if ship_text and "gratis" not in ship_text and "free" not in ship_text:
                        shipping_price = self._normalize_price(ship_text)
                    
                    total_price = float(price + shipping_price)

                    img_el = item.select_one(".s-item__image-img, .s-card__image-img, img")
                    image_url = img_el.get("src") if img_el else None

                    offers.append(ScrapedOffer(
                        product_name=title_raw,
                        price=price,
                        shipping_price=shipping_price,
                        total_price=total_price,
                        url=url,
                        shop_name=self.shop_name,
                        image_url=image_url,
                        source_type="Peer-to-Peer", 
                        sale_type="Fixed_P2P",
                        first_seen_at=datetime.utcnow()
                    ))
                    self.items_scraped += 1
                except:
                    continue
            
            if offers:
                self._log(f"✅ [Sirius-E Advanced] Capturadas {len(offers)} reliquias de élite.")
                return offers

        # 2. Escalamiento a Playwright si Sirius falla
        self._log("⚠️ [Sirius-E Advanced] Infiltración rápida fallida. Escalamiento táctico...", level="warning")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self._get_random_header()["User-Agent"],
                locale="es-ES"
            )
            page = await context.new_page()
            
            try:
                self._log(f"🧭 Navegando a resultados via Playwright (Advanced): {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(3)
                await self._stealth_scroll(page)
                
                # Infiltración de Profundidad (Fallback - Support Grid/List + Shipping)
                html = await page.content()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                items = soup.select(".s-item__wrapper, li.s-item, li.s-card")
                
                for item in items:
                    try:
                        title_raw = re.sub(r'(?i)(Nuevo anuncio|Se abre en una nueva ventana|o pestaña)', '', title_el.get_text(strip=True)).strip()
                        title = title_raw.lower()
                        
                        if "origins" not in title: continue

                        # Criba Sirius-E (Calibrada)
                        is_used = any(x in full_text for x in ["usado", "used", "segunda mano"])
                        if is_used and "nuevo" not in full_text: continue

                        price_el = item.select_one(".s-item__price, .s-card__price")
                        price = self._normalize_price(price_el.get_text()) if price_el else 0.0
                        
                        if price <= 0: continue

                        # Inteligencia de Envío (Phase 42 - Robust)
                        ship_el = item.select_one(".s-item__shipping, .s-card__shipping, .s-item__logisticsCost, .su-styled-text.secondary.large")
                        ship_text = ship_el.get_text().lower() if ship_el else ""
                        
                        # Fallback a búsqueda de texto si el selector falla
                        if not ship_text or ("envío" not in ship_text and "shipping" not in ship_text and "gratis" not in ship_text):
                            for span in item.find_all("span"):
                                txt = span.get_text().lower()
                                if "envío" in txt or "shipping" in txt:
                                    ship_text = txt
                                    break

                        shipping_price = 0.0
                        if ship_text and "gratis" not in ship_text and "free" not in ship_text:
                            shipping_price = self._normalize_price(ship_text)
                        
                        total_price = float(price + shipping_price)

                        url_el = item.select_one(".s-item__link, .s-card__link")
                        url = url_el.get("href").split("?")[0] if url_el else ""

                        img_el = item.select_one(".s-item__image-img, .s-card__image-img, img")
                        image_url = img_el.get("src") if img_el else None

                        offers.append(ScrapedOffer(
                            product_name=title_raw,
                            price=price,
                            shipping_price=shipping_price,
                            total_price=total_price,
                            url=url,
                            shop_name=self.shop_name,
                            image_url=image_url,
                            source_type="Peer-to-Peer", 
                            sale_type="Fixed_P2P",
                            first_seen_at=datetime.utcnow(),
                            is_sold=False
                        ))
                        self.items_scraped += 1
                    except:
                        continue
                
                self._log(f"✅ [Sirius-E Advanced] Playwright extrajo {len(offers)} items.")
            except Exception as e:
                self._log(f"❌ Error en Black Oracle Playwright: {e}", level="error")
            finally:
                await browser.close()
                
        return offers

    def _normalize_price(self, price_str: str) -> float:
        """Sincronizado con Base para evitar discrepancias."""
        try:
            # Eliminar todo lo que no sea dígitos o separadores decimales
            cleaned = re.sub(r'[^\d,.]', '', price_str)
            if ',' in cleaned and '.' in cleaned:
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                parts = cleaned.split(',')
                if len(parts[-1]) == 2: cleaned = cleaned.replace(',', '.')
                else: cleaned = cleaned.replace(',', '')
            return float(cleaned)
        except:
            return 0.0

    async def _stealth_scroll(self, page: Page):
        """Scroll humano para cargar contenido dinámico y cookies."""
        for _ in range(random.randint(2, 4)):
            await page.mouse.wheel(0, random.randint(400, 800))
            await asyncio.sleep(random.uniform(0.3, 0.7))

    async def _extract_item_links(self, page: Page) -> List[str]:
        return await page.evaluate('''() => {
            const links = new Set();
            document.querySelectorAll("a").forEach(a => {
                if (a.href && a.href.includes("/itm/")) {
                    // Limpieza de parámetros de tracking de eBay
                    const cleanUrl = a.href.split("?")[0];
                    // Aceptar cualquier dominio de eBay que contenga la ficha del item
                    if (cleanUrl.includes("/itm/")) {
                        links.add(cleanUrl);
                    }
                }
            });
            return Array.from(links);
        }''')

    async def _extract_advanced_details(self, page: Page, url: str) -> Optional[ScrapedOffer]:
        self._log(f"🧪 [Spider 2] Analizando ficha: {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        except:
            return None
        
        # Selectores en Cascada (Cascading Selectors V2) con Criba de Calidad (Sift)
        data = await page.evaluate('''() => {
            const getPrice = () => {
                const selectors = ['.x-price-primary span', '#prcIsum', '.ux-textspans--ORANGE', '[data-testid="x-price-primary"]'];
                for (const s of selectors) {
                    const el = document.querySelector(s);
                    if (el && el.innerText.trim()) return el.innerText;
                }
                return null;
            };

            const getTitle = () => {
                return document.querySelector(".x-item-title__mainTitle span")?.innerText || 
                       document.querySelector("h1.x-item-title__mainTitle span")?.innerText;
            };
            
            const cond = document.querySelector(".ux-icon-text__text span")?.innerText || "";
            const bids = document.querySelector(".x-bid-count")?.innerText || "";
            // Ubicación en ficha profunda
            const loc = document.querySelector(".ux-labels-values--itemLocation .ux-textspans--SECONDARY")?.innerText || "";

            return {
                title: getTitle(),
                price_raw: getPrice(),
                price_approx_eur: document.querySelector('.x-price-approx__price span')?.innerText,
                img: document.querySelector(".ux-lens-image, .pip-s-img, .ux-image-magnify-main-img")?.src,
                condition: cond,
                is_auction: bids !== "",
                location: loc
            };
        }''')
        
        # Filtro de Calidad Advanced (Black Oracle)
        if not data['title']: return None
        
        is_origins = "origins" in data['title'].lower()
        is_new = any(x in data['condition'].lower() for x in ["nuevo", "new", "sealed"])
        is_eu = any(x in data['location'].lower() for x in ["españa", "spain", "alemania", "germany", "francia", "france", "italia", "italy", "unión europea", "eu"])
        
        if not (is_origins and is_new and is_eu and not data['is_auction']):
            return None
            
        # Priorizar Precio en EUR (Directo o Aproximado por eBay)
        price_eur = 0.0
        orig_price = data['price_raw']
        
        if "€" in orig_price or "EUR" in orig_price:
            price_eur = self._normalize_price(orig_price)
            self._log(f"💶 Precio directo en EUR: {price_eur}€")
        elif data['price_approx_eur'] and ("€" in data['price_approx_eur'] or "EUR" in data['price_approx_eur']):
            price_eur = self._normalize_price(data['price_approx_eur'])
            self._log(f"🔄 Usando conversión de eBay: {price_eur}€ (Original: {orig_price})")
        else:
            # Fallback: Conversión manual solo si no hay rastro de EUR en la ficha
            val = self._normalize_price(orig_price)
            if "£" in orig_price or "GBP" in orig_price:
                price_eur = round(val * 1.20, 2)
                self._log(f"💷 Conversión manual GBP->EUR: {price_eur}€")
            elif "$" in orig_price or "USD" in orig_price:
                price_eur = round(val * 0.94, 2)
                self._log(f"💵 Conversión manual USD->EUR: {price_eur}€")
            else:
                price_eur = val
                self._log(f"❓ Moneda no identificada, usando valor crudo: {price_eur}")

        if price_eur <= 0: return None

        return ScrapedOffer(
            product_name=data['title'],
            price=price_eur,
            currency="EUR",
            url=url,
            shop_name="Ebay.es PRO",
            image_url=data['img'],
            source_type="Peer-to-Peer", 
            sale_type="Fixed_P2P",
            first_seen_at=datetime.utcnow(),
            is_sold=False
        )

    def _normalize_price(self, price_str: str) -> float:
        try:
            # Eliminar todo lo que no sea dígitos o separadores decimales
            cleaned = re.sub(r'[^\d,.]', '', price_str)
            # Manejar formatos internacionales (punto/coma)
            if ',' in cleaned and '.' in cleaned:
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                parts = cleaned.split(',')
                if len(parts[-1]) == 2: cleaned = cleaned.replace(',', '.')
                else: cleaned = cleaned.replace(',', '')
            return float(cleaned)
        except:
            return 0.0
