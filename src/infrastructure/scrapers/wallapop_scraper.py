"""
WallapopScraper: Versión basada en la API interna de Wallapop.
Fase 10.3 - Implementación nativa sin dependencias externas problemáticas.
Inspirado en WallaPy pero sin lxml.
"""
import asyncio
import logging
import httpx
import random
from typing import List
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class WallapopScraper(BaseScraper):
    """
    Scraper de Wallapop usando la API interna con rotación de User-Agents.
    """
    
    # Endpoint de búsqueda (mismo que usa la app móvil)
    API_URL = "https://api.wallapop.com/api/v3/general/search"
    
    # Pool de User-Agents para rotación
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    def __init__(self):
        super().__init__(shop_name="Wallapop", base_url="https://es.wallapop.com")
        self.is_auction_source = True # DNA Segregation (Phase 14)
    
    def _get_headers(self) -> dict:
        """Genera headers con User-Agent aleatorio."""
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "X-DeviceOS": "0",  # 0 = Web
            "X-Source": "web_search",
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
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(
                    timeout=30.0,
                    follow_redirects=True
                ) as client:
                    response = await client.get(
                        self.API_URL,
                        params=params,
                        headers=self._get_headers()
                    )
                    
                    if response.status_code == 403:
                        logger.warning(f"[{self.spider_name}] 403 en intento {attempt+1}, reintentando...")
                        await asyncio.sleep(random.uniform(1, 3))
                        continue
                    
                    if response.status_code != 200:
                        logger.error(f"[{self.spider_name}] API respondio con: {response.status_code}")
                        continue
                    
                    data = response.json()
                    items = data.get("search_objects", [])
                    logger.info(f"[{self.spider_name}] API devolvio {len(items)} items.")
                    
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
                                    shop_name=self.shop_name,
                                    image_url=image_url
                                ))
                                self.items_scraped += 1
                                
                        except Exception as e:
                            logger.warning(f"[{self.spider_name}] Error parseando item: {e}")
                            continue
                    
                    # Si llegamos aqui, exito
                    break
                    
            except httpx.TimeoutException:
                logger.error(f"[{self.spider_name}] Timeout en intento {attempt+1}")
            except Exception as e:
                logger.error(f"[{self.spider_name}] Error en intento {attempt+1}: {e}")
            
            await asyncio.sleep(random.uniform(1, 2))
        
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
