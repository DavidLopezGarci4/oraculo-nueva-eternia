import asyncio
import logging
import re
from typing import List, Optional
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)


class LaMansionDelTerrorScraper(BaseScraper):
    """
    Scraper for La Mansion del Terror (lamansiondelterror.es).
    curl-cffi fast path; Playwright fallback.
    """

    def __init__(self):
        super().__init__(shop_name="LaMansionDelTerror", base_url="https://lamansiondelterror.es")
        self.search_base = "https://lamansiondelterror.es/es/busqueda?q="

    async def search(self, query: str) -> List[ScrapedOffer]:
        self._log(f"🕵️‍♂️ Iniciando búsqueda en La Mansión del Terror para: {query}")

        search_term = query if query and query != "auto" else "masters of the universe origins"
        encoded = search_term.replace(" ", "+")

        offers = await self._scrape_all_pages_curl(encoded)

        if not offers:
            self._log("🎭 Fallback: Iniciando Playwright...")
            offers = await self._scrape_all_pages_playwright(encoded)

        self.items_scraped = len(offers)
        self._log(f"✅ Total ofertas La Mansión del Terror: {len(offers)}")
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
            self._log(f"📄 Página {page_num}: {len(page_offers)} productos en stock")

            # Check total pages from active page text
            soup = BeautifulSoup(html, "html.parser")
            active_page_tag = soup.select_one(".pagination .page-link.active")
            if active_page_tag:
                text = active_page_tag.get_text(strip=True)
                match = re.search(r"de\s+(\d+)", text, re.I)
                if match:
                    total_pages = int(match.group(1))
                    if page_num >= total_pages:
                        break

            # Fallback check: if no next page arrow icon is present
            next_arrow = soup.select_one(".pagination i.fa-angle-right, .pagination i.fa-chevron-right")
            if not next_arrow:
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
                    self._log(f"📄 Playwright p{page_num}: {len(page_offers)} productos en stock")

                    soup = BeautifulSoup(html, "html.parser")
                    active_page_tag = soup.select_one(".pagination .page-link.active")
                    if active_page_tag:
                        text = active_page_tag.get_text(strip=True)
                        match = re.search(r"de\s+(\d+)", text, re.I)
                        if match:
                            total_pages = int(match.group(1))
                            if page_num >= total_pages:
                                break

                    next_arrow = soup.select_one(".pagination i.fa-angle-right, .pagination i.fa-chevron-right")
                    if not next_arrow:
                        break

                    await self._random_sleep(1.0, 2.5)

            except Exception as e:
                self._log(f"❌ Error Playwright La Mansión del Terror: {e}", level="error")
                self.errors += 1
            finally:
                await browser.close()

        return offers

    # ------------------------------------------------------------------
    # HTML parsing
    # ------------------------------------------------------------------
    def _parse_listing(self, html: str) -> List[ScrapedOffer]:
        soup = BeautifulSoup(html, "html.parser")
        products = soup.select(".product")
        offers: List[ScrapedOffer] = []

        for product in products:
            try:
                # 1. Stock / Availability Check
                # If product contains a badge containing "Agotado" or badge-danger class, discard it.
                is_agotado = False
                badges = product.select(".badge-ecommerce")
                for badge in badges:
                    badge_text = badge.get_text(strip=True).lower()
                    if "agotado" in badge_text:
                        is_agotado = True
                        break
                
                # Double check with badge-danger class
                if not is_agotado:
                    danger_badge = product.select_one(".badge-danger")
                    if danger_badge and "agotado" in danger_badge.get_text(strip=True).lower():
                        is_agotado = True

                if is_agotado:
                    # Discard out of stock items
                    continue

                # 2. Title + URL
                title_tag = product.select_one("h3 a")
                if not title_tag:
                    title_tag = product.select_one("a.text-color-hover-primary")
                if not title_tag:
                    continue
                name = title_tag.get_text(strip=True)
                link = title_tag.get("href") or ""
                if not link:
                    continue
                if not link.startswith("http"):
                    link = f"{self.base_url}{link}"

                # 3. Price
                # Current price (price paid by customer) is in class .sale
                sale_tag = product.select_one(".sale")
                if not sale_tag:
                    continue
                price_current = self._normalize_price(sale_tag.get_text(strip=True))
                if price_current == 0.0:
                    continue

                # Original price (present only if there is a discount) is in class .amount
                # We don't save original price directly into ScrapedOffer (since it doesn't have a field for it),
                # but we parse and log it, or save it to price if needed.
                # In ScrapedOffer, price must be the final selling price (current price).
                
                # 4. Image
                img_url: Optional[str] = None
                img_tag = product.select_one(".product-thumb-info-image img, img.img-fluid, img")
                if img_tag:
                    img_url = img_tag.get("src") or img_tag.get("data-src")
                if img_url and img_url.startswith("/"):
                    img_url = f"{self.base_url}{img_url}"

                offers.append(
                    ScrapedOffer(
                        product_name=name,
                        price=price_current,
                        url=link,
                        shop_name=self.spider_name,
                        image_url=img_url,
                        is_available=True, # Since we discarded "Agotado", they are available
                    )
                )
            except Exception as e:
                logger.warning(f"[{self.spider_name}] Error parsing product item: {e}")
                continue

        return offers
