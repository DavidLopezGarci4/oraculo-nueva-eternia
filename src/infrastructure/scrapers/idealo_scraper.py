import asyncio
import re
from typing import List
from bs4 import BeautifulSoup
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

class IdealoScraper(BaseScraper):
    """
    Idealo.es Scraper for MOTU Origins.
    Aggregates offers from multiple shops in a single stealthy pass.
    """
    def __init__(self):
        super().__init__(shop_name="Idealo.es", base_url="https://www.idealo.es")
        self.search_url = "https://www.idealo.es/resultados.html?q="

    async def search(self, query: str) -> List[ScrapedOffer]:
        """
        Searches Idealo.es for MOTU Origins items.
        """
        search_query = "masters of the universe origins" if query == "auto" else query
        url = f"{self.search_url}{search_query.replace(' ', '+')}"
        
        self._log(f"🌩️ Idealo.es: Descubriendo ofertas agregadas para '{search_query}'...")
        
        offers = []
        html = await self._curl_get(url, impersonate="chrome120")
        
        if not html:
            self._log("❌ Idealo.es: No se pudo obtener respuesta del agregador.", level="error")
            return []

        soup = BeautifulSoup(html, "html.parser")
        
        # Idealo usually uses 'offerList-item' or 'productTile'
        items = soup.select(".offerList-item, .productTile, .offer-list-item")
        self._log(f"📊 Idealo.es: Detectadas {len(items)} señales comerciales.")

        for item in items:
            try:
                # Title
                title_el = item.select_one(".offerList-item-description-title, .productTile-title, h3")
                title = title_el.get_text(strip=True) if title_el else "Unknown MOTU Item"
                
                # Price
                price_el = item.select_one(".offerList-item-price, .productTile-price, .price")
                price = self._normalize_price(price_el.get_text()) if price_el else 0.0
                
                # URL
                link_el = item.select_one("a")
                relative_url = link_el.get("href") if link_el else ""
                full_url = f"https://www.idealo.es{relative_url}" if relative_url.startswith("/") else relative_url
                
                # Image
                img_el = item.select_one("img")
                image_url = img_el.get("src") if img_el else None

                if price > 0:
                    offers.append(ScrapedOffer(
                        product_name=title,
                        price=price,
                        url=full_url,
                        shop_name="Idealo Aggregate",
                        image_url=image_url,
                        source_type="Retail"
                    ))
                    self.items_scraped += 1

            except Exception as e:
                continue
        
        return offers
