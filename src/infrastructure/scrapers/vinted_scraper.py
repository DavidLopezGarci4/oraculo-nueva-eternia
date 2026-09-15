import asyncio
import logging
import random
import re
import time
from typing import List, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class VintedScraper(BaseScraper):
    """
    Scraper de Vinted basado en la vista de catálogo SSR web.
    Requiere inicialización de sesión para evitar bloqueos y evasión perimetral.
    """
    
    CATALOG_URL = "https://www.vinted.es/catalog"
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    def __init__(self):
        super().__init__(shop_name="Vinted", base_url="https://www.vinted.es")
        self.is_auction_source = True
        self._session: Optional[AsyncSession] = None
        
    async def _init_session(self):
        """Inicializa la sesión visitando la home para obtener cookies."""
        if self._session is None:
            self._session = AsyncSession(impersonate="chrome120")
            
        ua = random.choice(self.USER_AGENTS)
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
        }
        
        try:
            # Petición a la home para "calentar" cookies
            self._log("🍪 Vinted: Inicializando sesión (Warm-up)...")
            await self._session.get(self.base_url, headers=headers, timeout=30)
            await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            self._log(f"⚠️ Error inicializando sesión de Vinted: {e}", level="warning")

    async def search(self, query: str) -> List[ScrapedOffer]:
        offers = []
        
        # 1. Configuración inteligente de palabras clave y límites de página
        if query == "auto":
            queries_config = [
                # Cuarteto Oficial de Búsquedas MOTU Origins
                ("motu origins", 2),
                ("masters of the universe origins", 2),
                ("he-man origins", 2),
                ("mattel origins", 2),
            ]
        else:
            queries_config = [(query, self.max_pages)]
            
        try:
            await self._init_session()
            
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
            }
            
            for search_query, pages_limit in queries_config:
                if self.blocked:
                    self._log("🛡️ Bloqueo activo. Saltando consultas restantes.", level="warning")
                    break
                    
                self._log(f"🕵️ Vinted Master Nexus: Buscando: {search_query} (Límite: {pages_limit} páginas)")
                
                try:
                    for page in range(1, pages_limit + 1):
                        params = {
                            "search_text": search_query,
                            "order": "newest_first",
                            "page": page
                        }
                        self._log(f"📄 Vinted: Escaneando '{search_query}' - Página {page}...")
                        
                        response = await self._session.get(self.CATALOG_URL, params=params, headers=headers, timeout=30)
                        
                        if response.status_code != 200:
                            self._log(f"⚠️ Vinted Error ({search_query} - Página {page}): {response.status_code}", level="warning")
                            if response.status_code in [403, 429]:
                                self.blocked = True
                                self._log("🛡️ Bloqueo detectado durante la búsqueda. Abortando esta consulta.", level="error")
                                break
                            break
                            
                        soup = BeautifulSoup(response.text, "html.parser")
                        overlay_links = soup.find_all("a", attrs={"data-testid": re.compile(r"^product-item-id-\d+--overlay-link$")})
                        
                        if not overlay_links:
                            self._log(f"🏁 Vinted: No hay más items para '{search_query}' en página {page}.")
                            break
                            
                        self._log(f"🎁 Vinted: Hallados {len(overlay_links)} items en página {page} para '{search_query}'.")
                        
                        for link in overlay_links:
                            try:
                                href = link.get("href", "")
                                title_attr = link.get("title", "")
                                test_id = link.get("data-testid", "")
                                
                                item_id_match = re.search(r"product-item-id-(\d+)", test_id)
                                item_id = item_id_match.group(1) if item_id_match else None
                                
                                # Extracción limpia de título
                                if ", Marca:" in title_attr:
                                    title = title_attr.split(", Marca:")[0].strip()
                                elif ", Estado:" in title_attr:
                                    title = title_attr.split(", Estado:")[0].strip()
                                else:
                                    slug_match = re.search(r"/items/\d+-([a-zA-Z0-9\-]+)", href)
                                    if slug_match:
                                        title = slug_match.group(1).replace("-", " ").title()
                                    else:
                                        title = title_attr.strip() or "Figura MOTU"
                                        
                                # Extracción de precio
                                price = None
                                if item_id:
                                    price_elem = soup.find(attrs={"data-testid": f"product-item-id-{item_id}--price-text"})
                                    if price_elem:
                                        raw_p = price_elem.get_text(strip=True).replace("€", "").replace("\xa0", "").strip()
                                        raw_p = raw_p.replace(",", ".")
                                        try:
                                            price = float(raw_p)
                                        except ValueError:
                                            pass
                                            
                                if price is None and title_attr:
                                    p_matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*€", title_attr)
                                    if p_matches:
                                        try:
                                            price = float(p_matches[0].replace(",", "."))
                                        except ValueError:
                                            pass
                                            
                                if not price or price <= 0:
                                    continue
                                    
                                clean_href = href.split("?")[0]
                                url = f"https://www.vinted.es{clean_href}" if clean_href.startswith("/") else clean_href
                                
                                # Extracción de imagen
                                image_url = None
                                if item_id:
                                    img_elem = soup.find("div", attrs={"data-testid": f"product-item-id-{item_id}--image"})
                                    if img_elem:
                                        img_tag = img_elem.find("img")
                                        if img_tag:
                                            image_url = img_tag.get("src")
                                            
                                offers.append(ScrapedOffer(
                                    product_name=title,
                                    price=price,
                                    url=url,
                                    shop_name="Vinted",
                                    image_url=image_url,
                                    source_type="Peer-to-Peer",
                                    sale_type="Fixed_P2P",
                                    first_seen_at=datetime.now(timezone.utc).replace(tzinfo=None),
                                    is_sold=False
                                ))
                                self.items_scraped += 1
                            except Exception as e:
                                logger.warning(f"Error parseando item de Vinted: {e}")
                        
                        # Retardo de cortesía entre páginas
                        await asyncio.sleep(random.uniform(2.0, 3.5))
                    
                    # Si quedan consultas por realizar, hacemos una pausa mayor
                    if not self.blocked:
                        await asyncio.sleep(random.uniform(3.0, 5.0))
                    
                except Exception as e:
                    self._log(f"⚠️ Error escaneando término '{search_query}': {e}", level="warning")
                    
        except Exception as e:
            self._log(f"❌ Error crítico en VintedScraper: {e}", level="error")
        finally:
            if self._session:
                await self._session.close()
                self._session = None
                
        return offers
