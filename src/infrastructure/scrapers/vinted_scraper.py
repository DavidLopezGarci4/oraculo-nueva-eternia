import asyncio
import logging
import random
import time
from typing import List, Optional
from datetime import datetime
from curl_cffi.requests import AsyncSession
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class VintedScraper(BaseScraper):
    """
    Scraper de Vinted basado en la API interna v2.
    Requiere inicialización de sesión para evitar bloqueos.
    """
    
    API_URL = "https://www.vinted.es/api/v2/catalog/items"
    
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
                # Foco Origins (Moderno)
                ("masters of the universe origins", 2),
                ("masters del universo origins", 2),
                ("motu origins", 2),
                
                # Foco Vintage (Clásicos de los 80 - muy específicos para evitar ruido)
                ("masters of the universe vintage", 2),
                ("masters del universo vintage", 2),
                ("motu vintage", 2),
                
                # Foco General (Bajo volumen de páginas para evitar spam/bloqueos)
                ("masters of the universe", 1),
                ("masters del universo", 1),
                ("motu", 1)
            ]
        else:
            queries_config = [(query, self.max_pages)]
            
        try:
            await self._init_session()
            
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "XMLHttpRequest"
            }
            
            for search_query, pages_limit in queries_config:
                if self.blocked:
                    self._log("🛡️ Bloqueo activo. Saltando consultas restantes.", level="warning")
                    break
                    
                params = {
                    "search_text": search_query,
                    "order": "newest_first",
                    "per_page": 50,
                    "currency": "EUR"
                }
                
                self._log(f"🕵️ Vinted Master Nexus: Buscando: {search_query} (Límite: {pages_limit} páginas)")
                
                try:
                    for page in range(1, pages_limit + 1):
                        params["page"] = page
                        self._log(f"📄 Vinted: Escaneando '{search_query}' - Página {page}...")
                        
                        response = await self._session.get(self.API_URL, params=params, headers=headers, timeout=30)
                        
                        if response.status_code != 200:
                            self._log(f"⚠️ Vinted API Error ({search_query} - Página {page}): {response.status_code}", level="warning")
                            if response.status_code in [403, 429]:
                                self.blocked = True
                                self._log("🛡️ Bloqueo detectado durante la búsqueda. Abortando esta consulta.", level="error")
                                break
                            break
                            
                        data = response.json()
                        items = data.get("items", [])
                        
                        if not items:
                            self._log(f"🏁 Vinted: No hay más items para '{search_query}' en página {page}.")
                            break
                            
                        self._log(f"🎁 Vinted: Hallados {len(items)} items en página {page} para '{search_query}'.")
                        
                        for item in items:
                            try:
                                title = item.get("title", "Figura MOTU")
                                price_data = item.get("price")
                                if isinstance(price_data, dict):
                                    price = float(price_data.get("amount", 0))
                                else:
                                    price = float(str(price_data).replace("€", "").replace(",", ".").replace(" ", "").strip())
                                
                                if price <= 0: continue
                                
                                item_id = item.get("id")
                                url = f"https://www.vinted.es/items/{item_id}"
                                
                                # Imagen
                                photos = item.get("photos", [])
                                image_url = photos[0].get("url") if photos else None
                                
                                offers.append(ScrapedOffer(
                                    product_name=title,
                                    price=price,
                                    url=url,
                                    shop_name="Vinted",
                                    image_url=image_url,
                                    source_type="Peer-to-Peer",
                                    sale_type="Fixed_P2P",
                                    first_seen_at=datetime.utcnow(),
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
