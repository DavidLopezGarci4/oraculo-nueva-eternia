import asyncio
import logging
from typing import List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class DVDStoreSpainScraper(BaseScraper):
    """
    Scraper for DVDStoreSpain.es 
    Architecture Phase 47: PrestaShop 1.7+ Specialist.
    """
    def __init__(self):
        super().__init__(shop_name="DVDStoreSpain", base_url="https://dvdstorespain.es")
        self.search_url = "https://dvdstorespain.es/es/buscar?controller=search&s="

    async def search(self, query: str) -> List[ScrapedOffer]:
        self._log(f"🕵️‍♂️ Iniciando búsqueda en DVDStoreSpain para: {query}")
        offers = []
        
        # Determine search term (fallback to masters for wide crawls)
        search_term = query if query and query != "auto" else "masters of the universe origins"
        url = f"{self.search_url}{search_term.replace(' ', '+')}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            headers = self._get_random_header()
            context = await browser.new_context(user_agent=headers["User-Agent"])
            page = await context.new_page()
            
            try:
                # Strategy: Go to Home and use the search bar (More resilient than direct GET)
                self._log("🏠 Navegando a la página principal para búsqueda UI...")
                if not await self._safe_navigate(page, self.base_url):
                    return []

                # Fill search
                search_input = "input[name='s']"
                await page.wait_for_selector(search_input)
                await page.fill(search_input, search_term)
                await page.press(search_input, "Enter")
                
                # Wait for results
                await asyncio.sleep(5) 
                
                title = await page.title()
                self._log(f"📄 Título post-búsqueda: {title}")
                
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # PrestaShop results container is usually #js-product-list or .product-miniature
                products = soup.select("article.product-miniature, .product-miniature")
                
                if not products:
                    self._log("🔎 No se detectaron productos. Verificando si hay redirección o si la búsqueda falló.")
                    # Sometimes search redirects to a single product if exact match
                    if "buscar" not in page.url:
                        self._log(f"🔀 Redirección detectada a: {page.url}")
                        # If we are in a product page, we might want to capture it as one result
                        # But for now, let's just log it.
                
                self._log(f"📦 Detectados {len(products)} productos potenciales.")

                for product in products:
                    try:
                        # 1. Title & URL
                        title_tag = product.select_one("h3.product-title a")
                        if not title_tag: continue
                        name = title_tag.get_text(strip=True)
                        link = title_tag.get("href")
                        if not link.startswith("http"):
                            link = f"{self.base_url}{link}"

                        # 2. Price
                        price_tag = product.select_one("span.price")
                        raw_price = price_tag.get_text(strip=True) if price_tag else "0"
                        price = self._normalize_price(raw_price)

                        # 3. Image
                        img_tag = product.select_one(".product-thumbnail img")
                        img_url = img_tag.get("src") if img_tag else None

                        # 4. EAN (PrestaShop often puts it in the URL slug or data attributes)
                        # We try to extract from the link if it contains a 13-digit sequence
                        ean = None
                        import re
                        ean_match = re.search(r'(\d{13})', link)
                        if ean_match:
                            ean = ean_match.group(1)

                        offer = ScrapedOffer(
                            product_name=name,
                            price=price,
                            url=link,
                            shop_name=self.shop_name,
                            image_url=img_url,
                            ean=ean,
                            is_available=True # PrestaShop listing usually implies stock unless it has "Agotado" flag
                        )
                        offers.append(offer)
                        
                    except Exception as e:
                        self._log(f"⚠️ Error procesando producto individual: {e}", level="debug")

                self.items_scraped = len(offers)
                self._log(f"✅ Extracción completada: {len(offers)} ofertas encontradas.")

            except Exception as e:
                self._log(f"❌ Error crítico en DVDStoreSpainScraper: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()

        return offers
