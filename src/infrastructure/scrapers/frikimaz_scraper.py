import asyncio
import logging
import re
from typing import List, Optional
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)


class FrikimazScraper(BaseScraper):
    """
    Scraper for Frikimaz.es (PrestaShop).
    curl-cffi fast path; Playwright fallback.
    """

    def __init__(self):
        super().__init__(shop_name="Frikimaz", base_url="https://frikimaz.es")
        self.search_base = "https://frikimaz.es/busqueda?controller=search&s="

    async def search(self, query: str) -> List[ScrapedOffer]:
        self._log(f"🕵️‍♂️ Iniciando búsqueda en Frikimaz para: {query}")

        search_term = query if query and query != "auto" else "masters of the universe"
        encoded = search_term.replace(" ", "+")

        offers = await self._scrape_all_pages_curl(encoded)

        if not offers:
            self._log("🎭 Fallback: Iniciando Playwright...")
            offers = await self._scrape_all_pages_playwright(encoded)

        self.items_scraped = len(offers)
        self._log(f"✅ Total ofertas Frikimaz: {len(offers)}")
        return offers

    # ------------------------------------------------------------------
    # STRATEGY 1: curl-cffi pagination
    # ------------------------------------------------------------------
    async def _scrape_all_pages_curl(self, encoded_query: str) -> List[ScrapedOffer]:
        offers: List[ScrapedOffer] = []

        for page_num in range(1, self.max_pages + 1):
            url = f"{self.search_base}{encoded_query}&page={page_num}"
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
            next_link = soup.select_one("a[rel='next'], .pagination a.next, li.next a")
            if not next_link:
                break

            await self._random_sleep(0.8, 2.0)

        return offers

    # ------------------------------------------------------------------
    # STRATEGY 2: Playwright fallback
    # ------------------------------------------------------------------
    async def _scrape_all_pages_playwright(self, encoded_query: str) -> List[ScrapedOffer]:
        from playwright.async_api import async_playwright

        offers: List[ScrapedOffer] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._get_random_header()["User-Agent"]
            )
            page = await context.new_page()

            try:
                for page_num in range(1, self.max_pages + 1):
                    url = f"{self.search_base}{encoded_query}&page={page_num}"
                    if not await self._safe_navigate(page, url):
                        break

                    await asyncio.sleep(2.0)
                    html = await page.content()
                    page_offers = self._parse_listing(html)

                    if not page_offers:
                        break

                    offers.extend(page_offers)
                    self._log(f"📄 Playwright p{page_num}: {len(page_offers)} productos")

                    soup = BeautifulSoup(html, "html.parser")
                    if not soup.select_one("a[rel='next'], .pagination a.next, li.next a"):
                        break

                    await self._random_sleep(1.0, 2.5)

            except Exception as e:
                self._log(f"❌ Error Playwright Frikimaz: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()

        return offers

    # ------------------------------------------------------------------
    # HTML parsing
    # ------------------------------------------------------------------
    def _parse_listing(self, html: str) -> List[ScrapedOffer]:
        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("article.product-miniature")
        offers: List[ScrapedOffer] = []

        for product in products:
            try:
                # Title + URL
                title_tag = product.select_one("h2.h3.product-title a, .product-title a")
                if not title_tag:
                    continue
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href") or ""
                if not link:
                    thumb = product.select_one("a.thumbnail.product-thumbnail")
                    link = thumb.get("href", "") if thumb else ""
                if not link:
                    continue
                if not link.startswith("http"):
                    link = f"{self.base_url}{link}"

                # Price
                price_tag = product.select_one("span.price")
                raw_price = price_tag.get_text(strip=True) if price_tag else "0"
                price = self._normalize_price(raw_price)
                if price == 0.0:
                    continue

                # Image
                img_url: Optional[str] = None
                thumb_block = product.select_one("a.thumbnail.product-thumbnail")
                if thumb_block:
                    img_tag = thumb_block.find("img")
                    if img_tag:
                        img_url = img_tag.get("src") or img_tag.get("data-src")
                if img_url and img_url.startswith("/"):
                    img_url = f"{self.base_url}{img_url}"

                # Availability — presence of out_of_stock flag = unavailable
                is_available = not bool(
                    product.select_one("li.product-flag.out_of_stock, .product-flag.out-of-stock")
                )

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
            except Exception:
                continue

        return offers

    async def _fetch_ean(self, product_url: str) -> Optional[str]:
        """Fetch EAN13 from the product detail page data-sheet section."""
        html = await self._curl_get(product_url)
        if not html:
            return None
        try:
            soup = BeautifulSoup(html, "html.parser")
            data_sheet = soup.select_one("section.product-features dl.data-sheet")
            if not data_sheet:
                return None
            dts = data_sheet.select("dt.name")
            for dt in dts:
                if "ean" in dt.get_text(strip=True).lower():
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        ean_val = dd.get_text(strip=True)
                        if re.match(r"^\d{8,13}$", ean_val):
                            return ean_val
        except Exception:
            pass
        return None
