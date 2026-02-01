import asyncio
import logging
import re
import xml.etree.ElementTree as ET
from typing import List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class DVDStoreSpainScraper(BaseScraper):
    """
    Scraper for DVDStoreSpain.es 
    Architecture Phase 47: PrestaShop 1.7+ Specialist.
    Integrated High-Precision Sitemap Fallback for Toys.
    """
    def __init__(self):
        super().__init__(shop_name="DVDStoreSpain", base_url="https://dvdstorespain.es")
        self.search_url = "https://dvdstorespain.es/es/buscar?controller=search&s="
        self.sitemap_urls = [
            "https://dvdstorespain.es/1_es_0_sitemap.xml",
            "https://dvdstorespain.es/1_es_1_sitemap.xml"
        ]

    async def search(self, query: str) -> List[ScrapedOffer]:
        self._log(f"🕵️‍♂️ Iniciando búsqueda en DVDStoreSpain para: {query}")
        
        # Determine search term
        search_term = query if query and query != "auto" else "masters of the universe origins"
        search_url = f"{self.base_url}/es/buscar?controller=search&s={search_term.replace(' ', '+')}"
        
        # --- STRATEGY 1: curl-cffi (Fast & Stealthy) ---
        self._log("🌩️ Intentando extracción rápida vía curl-cffi...")
        html = await self._curl_get(search_url)
        offers = []
        if html:
            offers = self._parse_html_results(html)
            # Filter and validate relevance
            offers = self._filter_relevant_offers(offers, search_term)
            
            if self._is_highly_relevant(offers, search_term):
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
                
                # Fill search
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
                offers = self._filter_relevant_offers(offers, search_term)
                
                if not self._is_highly_relevant(offers, search_term):
                    # Final try with BROAD search
                    if search_term != "masters":
                        self._log("🔎 Reintentando con término ultra-amplio 'masters'...")
                        await page.goto(f"{self.base_url}/es/buscar?controller=search&s=masters")
                        await asyncio.sleep(3)
                        final_html = await page.content()
                        offers = self._parse_html_results(final_html)
                        offers = self._filter_relevant_offers(offers, "masters")

            except Exception as e:
                self._log(f"❌ Error en Playwright: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()

        # --- STRATEGY 3: Sitemap-Backed Precision Search (The "Eternia" Shield) ---
        if not self._is_highly_relevant(offers, search_term):
            self._log("🗺️ Fallback Crítico: El buscador falló o es impreciso. Iniciando búsqueda en Sitemaps...")
            sitemap_offers = await self._sitemap_search(search_term)
            if sitemap_offers:
                offers = sitemap_offers
                self._log(f"🛡️ Éxito vía Sitemap: {len(offers)} ofertas de alta precisión encontradas.")

        self.items_scraped = len(offers)
        return offers

    def _filter_relevant_offers(self, offers: List[ScrapedOffer], query: str) -> List[ScrapedOffer]:
        """Prunes the results to only keep those that match key query keywords."""
        if not offers: return []
        # Stricter keywords: at least 4 chars or essential specific terms
        essential = ["motu", "he-man", "origins"]
        keywords = [k.lower() for k in query.lower().split() if len(k) > 3 or k.lower() in essential]
        if not keywords: keywords = [query.lower()]
        
        filtered = []
        for o in offers:
            name = o.product_name.lower()
            # Must match at least ONE relevant keyword AND be in merchandising if possible
            if any(k in name for k in keywords):
                # If we are looking for "origins", don't return random movies unless they have "origins"
                if "origins" in query.lower() and "origins" not in name and "merchandising" not in o.url.lower():
                    continue
                filtered.append(o)
        
        return filtered

    def _is_highly_relevant(self, offers: List[ScrapedOffer], query: str) -> bool:
        """Determines if the results are high quality enough to skip sitemap fallback."""
        if not offers: return False
        
        essential = ["motu", "he-man", "origins", "masterverse", "eternia", "skeletor"]
        query_keywords = [k.lower() for k in query.lower().split() if len(k) > 3 or k.lower() in essential]
        
        # If the user asked for "origins", we MUST find items with "origins" in the name
        needs_origins = "origins" in query.lower()
        found_origins = False
        
        exact_matches = 0
        for o in offers:
            name = o.product_name.lower()
            url = o.url.lower()
            
            # Count matches of essential words
            matches = sum(1 for k in query_keywords if k in name)
            
            # If it's merchandising and matches at least 2 key words, it's good
            if "merchandising" in url and matches >= 2:
                exact_matches += 1
                if "origins" in name:
                    found_origins = True

        if needs_origins and not found_origins:
            return False # Keep searching (sitemap) if we don't have origins specifically
            
        # If we found at least 2 high-quality merchandising matches
        return exact_matches >= 2

    async def _sitemap_search(self, query: str) -> List[ScrapedOffer]:
        """Performs a direct keyword search across all sitemaps."""
        keywords = query.lower().split()
        matching_urls = []
        
        self._log(f"🔎 Escaneando sitemaps para: {keywords}")
        
        for s_url in self.sitemap_urls:
            try:
                content = await self._curl_get(s_url)
                if not content: continue
                
                root = ET.fromstring(content.encode('utf-8') if isinstance(content, str) else content)
                ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for loc in root.findall('.//s:loc', ns):
                    loc_url = loc.text
                    # Priority for merchandising category
                    if "merchandising" in loc_url.lower():
                        if all(k in loc_url.lower() for k in keywords):
                            matching_urls.append(loc_url)
                        elif sum(1 for k in keywords if k in loc_url.lower()) >= 2:
                             matching_urls.append(loc_url)
            except Exception as e:
                self._log(f"⚠️ Error procesando sitemap {s_url}: {e}")

        # Limit results to avoid massive crawling
        unique_urls = list(dict.fromkeys(matching_urls))[:15]
        self._log(f"📍 Encontradas {len(unique_urls)} URLs candidatas en sitemap.")
        
        offers = []
        for url in unique_urls:
            offer = await self._parse_product_page(url)
            if offer:
                offers.append(offer)
            await asyncio.sleep(0.5) # Anti-ban friendly
            
        return offers

    async def _parse_product_page(self, url: str) -> Optional[ScrapedOffer]:
        """Extracts offer details from a direct product page."""
        html = await self._curl_get(url)
        if not html: return None
        
        soup = BeautifulSoup(html, 'html.parser')
        try:
            # 1. Title
            title_tag = soup.select_one("h1.h1, .product-detail-name")
            if not title_tag: return None
            name = title_tag.get_text(strip=True)
            
            # 2. Price
            price_tag = soup.select_one(".current-price span, [itemprop='price'], .price")
            raw_price = price_tag.get_text(strip=True) if price_tag else "0"
            price = self._normalize_price(raw_price)
            
            # 3. Image
            img_tag = soup.select_one(".product-cover img, .js-qv-product-cover")
            img_url = img_tag.get("src") if img_tag else None
            if not img_url and img_tag:
                 img_url = img_tag.get("data-full-size-image-url")
            
            # 4. EAN
            ean = None
            ean_match = re.search(r'(\d{13})', url)
            if ean_match: ean = ean_match.group(1)
            
            # 5. Availability
            availability_tag = soup.select_one("#product-availability")
            is_available = "disponible" in availability_tag.get_text(strip=True).lower() if availability_tag else True
            if "disponible" not in (availability_tag.text.lower() if availability_tag else "disponible"):
                # Check for "add to cart" existence as a fallback for availability
                is_available = soup.select_one(".add-to-cart") is not None

            return ScrapedOffer(
                product_name=name,
                price=price,
                url=url,
                shop_name=self.shop_name,
                image_url=img_url,
                ean=ean,
                is_available=is_available
            )
        except Exception as e:
            self._log(f"⚠️ Error parseando página de producto {url}: {e}")
            return None

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
