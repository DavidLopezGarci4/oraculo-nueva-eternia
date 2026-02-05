"""
WallapopScraper: Versión basada en la API interna de Wallapop.
Fase 10.3 - Implementación nativa sin dependencias externas problemáticas.
Inspirado en WallaPy pero sin lxml.
"""
import asyncio
import logging
from curl_cffi.requests import AsyncSession
import random
import time
from typing import List
from datetime import datetime
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer
from src.infrastructure.scrapers.wallapop_signer import WallapopSigner

logger = logging.getLogger(__name__)

class WallapopScraper(BaseScraper):
    """
    Scraper de Wallapop usando la API interna con X-Signature y rotación de User-Agents.
    """
    
    # Endpoint de búsqueda (mismo que usa la app móvil)
    API_URL = "https://api.wallapop.com/api/v3/general/search"
    
    # Pool de User-Agents para rotación
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    
    def __init__(self):
        super().__init__(shop_name="Wallapop", base_url="https://es.wallapop.com")
        self.is_auction_source = True # DNA Segregation (Phase 14)
        self.signer = WallapopSigner()
        self._session: Optional[AsyncSession] = None
    
    async def _init_session(self):
        """Inicializa la sesión visitando la home para obtener cookies."""
        if self._session is None:
            # Safari suele ser menos fiscalizado por algunos WAFs de Cloudfront
            self._session = AsyncSession(impersonate="safari15_5")
            
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-es",
            "Connection": "keep-alive"
        }
        
        try:
            self._log("🍪 Wallapop: Inicializando sesión (Perfil Safari)...")
            await self._session.get(self.base_url, headers=headers, timeout=30)
            await asyncio.sleep(random.uniform(2, 4))
        except Exception as e:
            self._log(f"⚠️ Error inicializando sesión de Wallapop: {e}", level="warning")
    
    def _get_headers(self, method: str, path: str) -> dict:
        """Genera headers con X-Signature y User-Agent aleatorio."""
        timestamp = int(time.time() * 1000)
        signature, _ = self.signer.generate_signature(method, path, timestamp)
        
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "X-DeviceOS": "0",  # 0 = Web
            "X-Source": "web_search",
            "X-Signature": signature,
            "X-Timestamp": str(timestamp),
            "User-Agent": random.choice(self.USER_AGENTS),
            "Origin": "https://es.wallapop.com",
            "Referer": "https://es.wallapop.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
    
    async def search(self, query: str) -> List[ScrapedOffer]:
        """
        Busca productos en Wallapop usando la API interna.
        """
        logger.info(f"[{self.spider_name}] Iniciando busqueda para: {query}")
        offers = []
        
        # Coordenadas de Madrid (centro de Espana para cobertura amplia)
        params = {
            "keywords": query,
            "latitude": 40.4168,
            "longitude": -3.7038,
            "order_by": "newest",
            "items_count": 40,
            "density_type": "20",
            "filters_source": "search_box",
            "country_code": "ES"
        }
        
        # Reintentos con diferentes User-Agents
        for page in range(self.max_pages):
            offset = page * 40
            params["offset"] = str(offset)
            
            self._log(f"📄 Wallapop: Escaneando página {page+1} (Offset: {offset})...")
            
            for attempt in range(3):
                try:
                    await self._init_session()
                    
                    # El path para la firma debe ser /api/v3/general/search
                    path_for_sig = "/api/v3/general/search"
                    
                    # Sincronizar headers de la sesión con los específicos de la firma
                    headers = self._get_headers("GET", path_for_sig)
                    
                    response = await self._session.get(
                        self.API_URL,
                        params=params,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 403:
                        logger.warning(f"[{self.spider_name}] 403 en intento {attempt+1}, reintentando con nueva sesión...")
                        self._session = None # Reset session to get new cookies
                        await asyncio.sleep(random.uniform(3, 7))
                        continue
                        
                    if response.status_code != 200:
                        logger.error(f"[{self.spider_name}] API respondio con: {response.status_code}")
                        break
                        
                    data = response.json()
                    items = data.get("search_objects", [])
                    
                    if not items:
                        self._log(f"🏁 Wallapop: No hay más items en offset {offset}. Fin.")
                        return offers
                        
                    self._log(f"🎁 Wallapop: Hallados {len(items)} items.")
                    
                    for item in items:
                        try:
                            item_id = item.get("id", "")
                            title = item.get("title", "Producto")
                            
                            # Precio
                            price_data = item.get("price", {})
                            if isinstance(price_data, dict):
                                price = float(price_data.get("amount", 0))
                            else:
                                price = float(price_data) if price_data else 0.0
                            
                            # URL
                            web_slug = item.get("web_slug", item_id)
                            url = f"https://es.wallapop.com/item/{web_slug}"
                            
                            # Imagen
                            images = item.get("images", [])
                            image_url = images[0].get("medium", "") if images else None
                            
                            if price > 0:
                                offers.append(ScrapedOffer(
                                    product_name=f"[Wallapop] {title}",
                                    price=price,
                                    currency="EUR",
                                    url=url,
                                    shop_name=self.spider_name,
                                    image_url=image_url,
                                    source_type="Peer-to-Peer",
                                    sale_type="Fixed_P2P",
                                    first_seen_at=datetime.utcnow(),
                                    is_sold=False
                                ))
                                self.items_scraped += 1
                                
                        except Exception as e:
                            logger.warning(f"[{self.spider_name}] Error parseando item: {e}")
                            continue
                    
                    # Si llegamos aquí, éxito en esta página. Descanso antes de la siguiente.
                    await asyncio.sleep(random.uniform(2, 5))
                    break
                    
                except Exception as e:
                    logger.error(f"[{self.spider_name}] Error en intento {attempt+1}: {e}")
                    await asyncio.sleep(random.uniform(2, 4))
        
        logger.info(f"[{self.spider_name}] Scraping finalizado. Total ofertas: {len(offers)}")
        return offers


if __name__ == "__main__":
    async def run_test():
        print("=" * 60)
        print(">>> TEST DE WALLAPOP (API v2) <<<")
        print("=" * 60)
        
        scraper = WallapopScraper()
        results = await scraper.search("motu origins")
        print(f"\n>>> ENCONTRADOS: {len(results)} items <<<\n")
        
        for i, o in enumerate(results[:10], 1):
            print(f"{i}. {o.product_name}")
            print(f"   Precio: {o.price} EUR")
            print(f"   URL: {o.url}")
            print("-" * 40)

    asyncio.run(run_test())
