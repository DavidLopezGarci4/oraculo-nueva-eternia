from typing import List, Optional
import asyncio
import logging
import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class BixotoScraper(BaseScraper):
    """
    Scraper para Bixoto (Tienda Online de Juguetes / Juegos en Francia/España).
    Extracción ultrarrápida (SvelteKit SSR) para reliquias Masters of the Universe: Origins.
    
    Características clave:
    - Búsqueda directa enfocada a MOTU Origins (Mattel).
    - Extracción de códigos de barras EAN-13 (GTIN-13) para matching determinista.
    - Tarifas logísticas: 3.99€ base a España, gratis a partir de 69.00€.
    """

    def __init__(self):
        super().__init__(
            shop_name="Bixoto",
            base_url="https://bixoto.com/es/u/games?search=masters+of+the+universe+origins&brands=mattel"
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        products: List[ScrapedOffer] = []
        seen_urls = set()

        # 1. Resolver URL de búsqueda
        if query and query not in ("auto", "*"):
            encoded = urllib.parse.quote_plus(query)
            target_url = f"https://bixoto.com/es/u/games?search={encoded}&brands=mattel"
        else:
            target_url = self.base_url

        self._log(f"🧭 [{self.spider_name}] Iniciando incursión en Bixoto...")
        logger.info(f"[{self.spider_name}] Scraping target: {target_url}")

        page_num = 1
        max_pages = 5

        while target_url and page_num <= max_pages:
            current_url = f"{target_url}&page={page_num}" if page_num > 1 else target_url
            self._log(f"📡 [{self.spider_name}] Accediendo a página {page_num}...")

            html = await self._curl_get(current_url)
            if not html:
                # Fallback nativo ligero con urllib si _curl_get falla o no está disponible
                try:
                    req = urllib.request.Request(
                        current_url,
                        headers=self._get_random_header()
                    )
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        html = resp.read().decode('utf-8', errors='ignore')
                except Exception as e:
                    self._log(f"⚠️ [{self.spider_name}] Error conectando a {current_url}: {e}", level="warning")
                    break

            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.select('.product-card__top')
            if not cards:
                logger.info(f"[{self.spider_name}] No se encontraron más tarjetas en página {page_num}.")
                break

            # 2. Extraer mapa de EAN-13 desde los metadatos SvelteKit en scripts
            slug_ean_map = {}
            for m in re.finditer(r'slug:"([^"]+)".*?ean13s:\["([0-9]{13})"', html):
                slug, ean = m.group(1), m.group(2)
                if slug not in slug_ean_map:
                    slug_ean_map[slug] = ean

            page_items_count = 0
            for card in cards:
                try:
                    title_el = card.select_one('.product-card__name')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title:
                        continue

                    # Filtro MOTU Origins / Universo (Descartar items no relacionados)
                    t_lower = title.lower()
                    if not any(k in t_lower for k in ['masters', 'universe', 'origins', 'motu', 'skeletor', 'he-man']):
                        continue

                    # Extraer enlace canónico
                    link_el = card.find('a', href=lambda h: h and h.startswith('/es/p/'))
                    if not link_el:
                        continue
                    
                    href = link_el['href']
                    full_url = f"https://bixoto.com{href}" if href.startswith('/') else href
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)

                    # Extraer precio (especial > original > div general)
                    price_div = card.select_one('.price')
                    price_val = 0.0
                    if price_div:
                        special = price_div.select_one('.special')
                        original = price_div.select_one('.original')
                        if special:
                            price_val = self._normalize_price(special.get_text(strip=True))
                        elif original:
                            price_val = self._normalize_price(original.get_text(strip=True))
                        else:
                            price_val = self._normalize_price(price_div.get_text(strip=True))

                    if price_val <= 0.0:
                        continue

                    # Extraer imagen
                    img_el = card.find('img')
                    img_url = (img_el.get('src') or img_el.get('data-src')) if img_el else None

                    # Extraer EAN si está disponible por slug o en URL
                    slug_match = re.search(r'/es/p/([^/?#]+)', full_url)
                    extracted_slug = slug_match.group(1) if slug_match else ""
                    ean = slug_ean_map.get(extracted_slug)

                    offer = ScrapedOffer(
                        product_name=title,
                        price=price_val,
                        currency="EUR",
                        url=full_url,
                        shop_name=self.shop_name,
                        is_available=True,
                        image_url=img_url,
                        ean=ean,
                        shipping_price=3.99,
                        source_type="Retail",
                        sale_type="Retail"
                    )

                    products.append(offer)
                    self.items_scraped += 1
                    page_items_count += 1

                except Exception as parse_err:
                    logger.debug(f"[{self.spider_name}] Error parseando tarjeta: {parse_err}")
                    continue

            logger.info(f"[{self.spider_name}] Página {page_num}: {page_items_count} ofertas extraídas.")
            self._log(f"📦 [{self.spider_name}] Página {page_num}: {page_items_count} reliquias encontradas.")

            # Comprobar si hay paginación activa
            has_next = soup.find('a', href=re.compile(rf'page={page_num + 1}'))
            if not has_next or page_items_count == 0:
                break

            page_num += 1
            await self._random_sleep(0.5, 1.5)

        self._log(f"✅ [{self.spider_name}] Incursión finalizada. Total: {len(products)} reliquias capturadas.")
        return products
