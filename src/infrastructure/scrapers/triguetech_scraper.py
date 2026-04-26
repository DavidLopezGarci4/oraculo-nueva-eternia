import asyncio
import logging
import re
from typing import List, Optional
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)


class TriguetechScraper(BaseScraper):
    """
    Scraper for Triguetech.es (WooCommerce).
    """

    def __init__(self):
        super().__init__(shop_name="Triguetech", base_url="https://www.triguetech.es")
        # Base url for MOTU Origins catalog
        self.catalog_url = "https://www.triguetech.es/categoria-producto/motu/masters-del-universo-origins/"
        # Search URL if query is explicitly provided
        self.search_url = "https://www.triguetech.es/?s={}&post_type=product"

    async def search(self, query: str) -> List[ScrapedOffer]:
        self._log(f"🕵️‍♂️ Iniciando búsqueda en Triguetech para: {query}")

        if query and query.lower() != "auto":
            # Si el usuario o el sistema busca algo específico
            encoded = query.replace(" ", "+")
            start_url = self.search_url.format(encoded)
        else:
            # Si es 'auto', escaneamos directamente la categoría completa de MOTU Origins
            start_url = self.catalog_url

        offers = await self._scrape_all_pages_curl(start_url)

        self.items_scraped = len(offers)
        self._log(f"✅ Total ofertas Triguetech: {len(offers)}")
        return offers

    # ------------------------------------------------------------------
    # STRATEGY: curl-cffi pagination
    # ------------------------------------------------------------------
    async def _scrape_all_pages_curl(self, base_url: str) -> List[ScrapedOffer]:
        offers: List[ScrapedOffer] = []

        for page_num in range(1, self.max_pages + 1):
            if page_num == 1:
                url = base_url
            else:
                if "?" in base_url:
                    # For search results (?s=...)
                    url = f"{base_url}&paged={page_num}"
                else:
                    # For catalog (categoria-producto/...)
                    url = f"{base_url}page/{page_num}/"

            html = await self._curl_get(url)

            if not html:
                break

            page_offers = self._parse_listing(html)
            if not page_offers:
                break

            offers.extend(page_offers)
            self._log(f"📄 Página {page_num}: {len(page_offers)} productos")

            # Stop if no next page link
            soup = BeautifulSoup(html, "html.parser")
            # In WooCommerce, pagination usually has class 'next' and 'page-numbers'
            next_link = soup.select_one("a.next.page-numbers")
            if not next_link:
                break

            await self._random_sleep(0.8, 2.0)

        return offers

    # ------------------------------------------------------------------
    # HTML parsing
    # ------------------------------------------------------------------
    def _parse_listing(self, html: str) -> List[ScrapedOffer]:
        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("li.product.type-product")
        offers: List[ScrapedOffer] = []

        for product in products:
            try:
                # Title + URL
                title_tag = product.select_one(".woocommerce-loop-product__title a") or product.select_one(".woocommerce-loop-product__title")
                if not title_tag:
                    continue
                    
                name = title_tag.get_text(strip=True)
                
                # Try getting link from title or the image container
                link = ""
                if title_tag.name == "a":
                    link = title_tag.get("href", "")
                if not link:
                    media_container = product.select_one("a.ct-media-container")
                    link = media_container.get("href", "") if media_container else ""
                    
                if not link:
                    continue

                if not link.startswith("http"):
                    link = f"{self.base_url}{link}"

                # Price (WooCommerce structure)
                # First check for sale price <ins> element
                ins_price = product.select_one("ins .woocommerce-Price-amount.amount bdi")
                if ins_price:
                    raw_price = ins_price.get_text(strip=True)
                else:
                    # Then fallback to normal price
                    price_tag = product.select_one(".price .woocommerce-Price-amount.amount bdi")
                    raw_price = price_tag.get_text(strip=True) if price_tag else "0"

                price = self._normalize_price(raw_price)
                if price == 0.0:
                    continue

                # Image
                img_url: Optional[str] = None
                img_tag = product.select_one("a.ct-media-container img")
                if img_tag:
                    img_url = img_tag.get("src") or img_tag.get("data-src")
                    
                if img_url and img_url.startswith("/"):
                    img_url = f"{self.base_url}{img_url}"

                # Availability
                # WooCommerce products use classes on the li element: 'instock', 'outofstock', 'onbackorder'
                classes = product.get("class", [])
                
                # It is available if it's not explicitly out of stock
                is_available = "outofstock" not in classes

                offers.append(
                    ScrapedOffer(
                        product_name=name,
                        price=price,
                        url=link,
                        shop_name=self.shop_name,
                        image_url=img_url,
                        is_available=is_available,
                    )
                )
            except Exception as e:
                self._log(f"Error parseando item en Triguetech: {str(e)}", level="debug")
                continue

        return offers
