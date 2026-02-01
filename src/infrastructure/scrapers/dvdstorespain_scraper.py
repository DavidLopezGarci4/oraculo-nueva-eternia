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
        
        # Determine search term (simplify if too long for their engine)
        original_term = query if query and query != "auto" else "masters of the universe origins"
        search_term = original_term
        if len(search_term.split()) > 3:
            search_term = " ".join(search_term.split()[:3]) # "masters of the" or similar
            self._log(f"✂️ Simplificando búsqueda a: {search_term}")

        search_url = f"{self.base_url}/es/buscar?controller=search&s={search_term.replace(' ', '+')}"
        
        # --- STRATEGY 1: curl-cffi (Fast & Stealthy) ---
        self._log("🌩️ Intentando extracción rápida vía curl-cffi...")
        html = await self._curl_get(search_url)
        if html:
            offers = self._parse_html_results(html)
            if offers:
                self.items_scraped = len(offers)
                self._log(f"✅ Extracción exitosa vía curl-cffi: {len(offers)} ofertas.")
                return offers

        # --- STRATEGY 2: Playwright (Resilient Fallback) ---
        self._log("🎭 Fallback: Iniciando Playwright para navegación profunda...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            headers = self._get_random_header()
            context = await browser.new_context(user_agent=headers["User-Agent"])
            page = await context.new_page()
            
            try:
                # Go to home first
                await self._safe_navigate(page, self.base_url)
                
                # Fill search - Use visible selector to avoid hidden mobile inputs
                search_input_selector = "input[name='s']:visible"
                try:
                    await page.wait_for_selector(search_input_selector, timeout=8000)
                    await page.locator(search_input_selector).first.fill(search_term)
                    await page.keyboard.press("Enter")
                except:
                    self._log("⚠️ No se encontró input visible. Navegando directamente...")
                    await self._safe_navigate(page, search_url)

                # Wait for results
                await asyncio.sleep(4) 
                
                final_html = await page.content()
                offers = self._parse_html_results(final_html)
                
                if not offers:
                    # Final try with BROAD search if specific fails
                    if search_term != "masters":
                        self._log("🔎 Reintentando con término ultra-amplio 'masters'...")
                        await page.goto(f"{self.base_url}/es/buscar?controller=search&s=masters")
                        await asyncio.sleep(3)
                        final_html = await page.content()
                        offers = self._parse_html_results(final_html)

                self.items_scraped = len(offers)
                self._log(f"✅ Extracción completada: {len(offers)} ofertas encontradas.")

            except Exception as e:
                self._log(f"❌ Error crítico en Playwright fallback: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()

        return offers

    def _parse_html_results(self, html: str) -> List[ScrapedOffer]:
        """Helper to parse PrestaShop product list HTML."""
        offers = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # PrestaShop selectors
        products = soup.select("article.product-miniature, .product-miniature, [data-id-product]")
        
        for product in products:
            try:
                # 1. Title & URL
                title_tag = product.select_one("h3.product-title a, h2.product-title a, .product-title a")
                if not title_tag: continue
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href")
                if not link: continue
                if not link.startswith("http"):
                    link = f"{self.base_url}{link}"

                # 2. Price
                price_tag = product.select_one(".price, span.price, .current-price")
                raw_price = price_tag.get_text(strip=True) if price_tag else "0"
                price = self._normalize_price(raw_price)

                # 3. Image
                img_tag = product.select_one(".product-thumbnail img, .thumbnail img")
                img_url = img_tag.get("src") if img_tag else None
                if not img_url and img_tag:
                    img_url = img_tag.get("data-full-size-image-url")

                # 4. EAN Extraction
                ean = None
                import re
                ean_match = re.search(r'(\d{13})', link)
                if ean_match: ean = ean_match.group(1)

                offers.append(ScrapedOffer(
                    product_name=name,
                    price=price,
                    url=link,
                    shop_name=self.shop_name,
                    image_url=img_url,
                    ean=ean,
                    is_available=True
                ))
            except:
                continue
                
        return offers
