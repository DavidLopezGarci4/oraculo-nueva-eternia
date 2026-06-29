import asyncio
import logging
import random
import time
import re
import os
import tempfile
from typing import List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class WallapopScraper(BaseScraper):
    """
    Scraper de Wallapop Híbrido (API Directa / Apify / ScraperAPI / Playwright Fallback).
    Bypassa bloqueos WAF de CloudFront mediante una cascada inteligente de APIs gratuitas,
    rotación de proxies y automatización como último recurso.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]
    
    # Class-level variables to persist across scraper instances/runs in the uvicorn process
    global_failed_proxies = set()
    global_free_proxies = []
    global_apify_exhausted = False
    global_scraperapi_exhausted = False

    def __init__(self):
        super().__init__(shop_name="Wallapop", base_url="https://es.wallapop.com")
        self.is_auction_source = True # Peer-to-Peer
        
    async def _fetch_free_proxies(self, session: AsyncSession) -> List[str]:
        """
        Cosecha proxies públicos y frescos de Geonode y ProxyScrape de forma aleatorizada.
        """
        if WallapopScraper.global_free_proxies:
            return WallapopScraper.global_free_proxies

        self._log("📡 Cosechando proxies públicos para rotación...")
        proxies = []
        
        # 1. Intentar Geonode
        try:
            url_geonode = "https://proxylist.geonode.com/api/proxy-list?limit=40&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps"
            response = await session.get(url_geonode, timeout=3)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", []):
                    ip = item.get("ip")
                    port = item.get("port")
                    protocols = item.get("protocols", ["http"])
                    protocol = protocols[0] if protocols else "http"
                    proxies.append(f"{protocol}://{ip}:{port}")
        except Exception as e:
            self._log(f"⚠️ Error al obtener proxies de Geonode: {e}")
            
        # 2. Intentar ProxyScrape (como complemento)
        if len(proxies) < 15:
            try:
                url_ps = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=8000&country=all&ssl=all&anonymity=all"
                response = await session.get(url_ps, timeout=8)
                if response.status_code == 200:
                    text = response.text
                    lines = text.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line and ":" in line:
                            proxies.append(f"http://{line}")
            except Exception as e:
                self._log(f"⚠️ Error al obtener proxies de ProxyScrape: {e}")
                
        # Randomizar para evitar sobrecargar los mismos servidores
        random.shuffle(proxies)
        WallapopScraper.global_free_proxies = proxies
        self._log(f"✅ Cosecha finalizada. {len(WallapopScraper.global_free_proxies)} proxies listos para rotación.")
        return WallapopScraper.global_free_proxies

    def _parse_wallapop_json_objects(self, items: List[dict]) -> List[ScrapedOffer]:
        offers: List[ScrapedOffer] = []
        junk_keywords = ["camiseta", "t-shirt", "poster", "taza", "mug", "revista", "dvd", "llavero", "keyring", "reproduccion", "repro", "sticker", "pegatina"]
        
        for obj in items:
            title = obj.get("title")
            price = obj.get("price")
            
            if not title or price is None:
                continue
                
            # Parse price
            if isinstance(price, dict):
                price_val = float(price.get("amount", 0))
            else:
                try:
                    price_val = float(price)
                except ValueError:
                    continue
                    
            if price_val <= 0:
                continue
                
            # Filtro de ruido
            title_lower = title.lower()
            if any(kw in title_lower for kw in junk_keywords):
                continue
                
            slug = obj.get("web_slug")
            if not slug:
                continue
                
            full_url = f"https://es.wallapop.com/item/{slug}"
            
            # Image URL
            image_url = None
            images = obj.get("images", [])
            if images and isinstance(images, list):
                first_img = images[0]
                if isinstance(first_img, dict):
                    if "urls" in first_img and isinstance(first_img["urls"], dict):
                        urls = first_img["urls"]
                        image_url = urls.get("big") or urls.get("medium") or urls.get("small")
                    else:
                        image_url = first_img.get("original") or first_img.get("medium")
                else:
                    image_url = first_img
            elif obj.get("image"):
                img_obj = obj.get("image")
                if isinstance(img_obj, dict):
                    if "urls" in img_obj and isinstance(img_obj["urls"], dict):
                        urls = img_obj["urls"]
                        image_url = urls.get("big") or urls.get("medium") or urls.get("small")
                    else:
                        image_url = img_obj.get("original") or img_obj.get("medium")
                else:
                    image_url = img_obj
                    
            offer = ScrapedOffer(
                product_name=title,
                price=price_val,
                url=full_url,
                shop_name=self.shop_name,
                image_url=image_url,
                source_type="Peer-to-Peer",
                sale_type="Fixed_P2P"
            )
            offers.append(offer)
            
        return offers

    async def search_via_api(self, query: str, max_items: int = 40) -> List[ScrapedOffer]:
        """
        Intenta obtener las ofertas de Wallapop de forma directa y ultra-rápida.
        Utiliza una cascada inteligente de APIs con cuota gratuita (Apify -> ScraperAPI -> Directa/Proxies).
        """
        # --- FASE 1: APIFY (Créditos Gratuitos ~20,000 reqs/mes) ---
        apify_token = os.environ.get("APIFY_TOKEN")
        if apify_token and not WallapopScraper.global_apify_exhausted:
            self._log("📡 Cascading Scraper: Intentando con Apify Actor (Prioridad 1, Capa Gratuita)...")
            try:
                apify_url = f"https://api.apify.com/v2/acts/igolaizola~wallapop-scraper/run-sync-get-dataset-items?token={apify_token}"
                async with AsyncSession() as session:
                    apify_response = await session.post(
                        apify_url,
                        json={
                            "query": query, 
                            "maxItems": max_items,
                            "postalCode": "28001",
                            "orderBy": "newest"
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=120
                    )
                    
                    if apify_response.status_code in [200, 201]:
                        items = apify_response.json()
                        offers = self._parse_wallapop_json_objects(items)
                        self._log(f"🎉 Apify: ¡Éxito! Encontrados {len(offers)} objetos para '{query}'.")
                        return offers
                    elif apify_response.status_code in [402, 429]:
                        self._log("⚠️ Apify: Límite de cuota gratuita superado (HTTP 402/429). Marcando Apify como agotado.", level="warning")
                        WallapopScraper.global_apify_exhausted = True
                    else:
                        self._log(f"⚠️ Apify falló con código HTTP: {apify_response.status_code}", level="warning")
            except Exception as e:
                self._log(f"⚠️ Error al conectar con Apify: {e}", level="warning")
                
        # --- FASE 2: CONEXIÓN DIRECTA CON IMPERSONACIÓN O PROXIES ---
        self._log(f"⚡ Wallapop API: Iniciando secuencia de extracción para '{query}'...")
        async with AsyncSession() as session:
            user_agent = random.choice(self.USER_AGENTS)
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "User-Agent": user_agent,
                "Origin": "https://es.wallapop.com",
                "Referer": "https://es.wallapop.com/",
                "DeviceOS": "0",
                "X-DeviceOS": "0",
            }
            
            params = {
                "keywords": query,
                "order_by": "newest",
                "source": "search_box",
                "latitude": 40.416775,
                "longitude": -3.703790
            }
            
            try:
                import urllib.parse
                target_url = "https://api.wallapop.com/api/v3/general/search?" + urllib.parse.urlencode(params)
                
                scraperapi_key = os.environ.get("SCRAPERAPI_KEY")
                use_proxy = False
                is_production = os.environ.get("ENV") == "production"
                if os.environ.get("GITHUB_ACTIONS") == "true":
                    use_proxy = True
                elif is_production:
                    self._log("📡 Entorno de Producción (OCI/Docker) detectado. Saltando conexión directa (IP de Datacenter bloqueada por WAF por defecto).")
                    use_proxy = True
                    
                response = None
                
                # Intentar conexión directa primero (solo si no estamos obligados a usar proxy)
                if not use_proxy:
                    try:
                        self._log("⚡ Wallapop API: Intentando conexión directa...")
                        response = await session.get(
                            target_url,
                            headers=headers,
                            impersonate="chrome120",
                            timeout=15
                        )
                        if response.status_code in [403, 429]:
                            self._log(f"⚠️ Conexión directa bloqueada (HTTP {response.status_code}).")
                            use_proxy = True
                    except Exception as e:
                        self._log(f"⚠️ Falló conexión directa a Wallapop API: {e}")
                        use_proxy = True
                        
                # --- FASE 3: SCRAPERAPI PROXY (Prioridad 2, Capa Gratuita ~5,000 reqs/mes) ---
                if use_proxy and scraperapi_key and not WallapopScraper.global_scraperapi_exhausted:
                    try:
                        params_sa = {
                            "api_key": scraperapi_key,
                            "url": target_url,
                            "country_code": "es",
                            "premium": "true",
                            "render": "true"
                        }
                        scraperapi_url = f"http://api.scraperapi.com?{urllib.parse.urlencode(params_sa)}"
                        self._log("📡 Ruteando Wallapop API a través de ScraperAPI (Premium ES + Render)...")
                        response = await session.get(
                            scraperapi_url,
                            headers=headers,
                            timeout=90
                        )
                        if response.status_code in [403, 429]:
                            self._log(f"⚠️ ScraperAPI: Créditos agotados (HTTP {response.status_code}). Marcando ScraperAPI como agotado.", level="warning")
                            WallapopScraper.global_scraperapi_exhausted = True
                        elif response.status_code == 500:
                            self._log("⚠️ ScraperAPI falló con error HTTP 500.", level="warning")
                    except Exception as e:
                        self._log(f"⚠️ Error al conectar a ScraperAPI: {e}")
                        
                # --- FASE 4: ROTACIÓN DINÁMICA DE PROXIES PÚBLICOS (Último recurso API) ---
                if use_proxy and (not response or response.status_code != 200):
                    self._log("🌩️ Iniciando rotador dinámico de proxies públicos para Wallapop API...")
                    free_proxies = await self._fetch_free_proxies(session)
                    
                    if len(WallapopScraper.global_failed_proxies) > 3000:
                        self._log("🧹 Limpiando historial de proxies fallidos por exceso de tamaño.")
                        WallapopScraper.global_failed_proxies.clear()
                        
                    available_proxies = [p for p in free_proxies if p not in WallapopScraper.global_failed_proxies]
                    self._log(f"🌩️ {len(available_proxies)} proxies disponibles para probar (excluyendo {len(WallapopScraper.global_failed_proxies)} fallidos históricamente).")
                    
                    for proxy in available_proxies[:25]:
                        try:
                            self._log(f"📡 Probando proxy público: {proxy}...")
                            proxy_response = await session.get(
                                target_url,
                                headers=headers,
                                impersonate="chrome120",
                                proxy=proxy,
                                timeout=4
                            )
                            if proxy_response.status_code == 200:
                                self._log(f"🎉 ¡Éxito con proxy público: {proxy}!")
                                response = proxy_response
                                break
                            else:
                                self._log(f"❌ Proxy devolvió código: {proxy_response.status_code}")
                                WallapopScraper.global_failed_proxies.add(proxy)
                        except Exception as e:
                            self._log(f"❌ Proxy inalcanzable / lento (Error: {type(e).__name__})")
                            WallapopScraper.global_failed_proxies.add(proxy)
                            
                # Mapear respuesta
                if response and response.status_code == 200:
                    data = response.json()
                    search_objects = data.get("search_objects", [])
                    offers = self._parse_wallapop_json_objects(search_objects)
                    self._log(f"🎉 Wallapop API: Encontrados {len(offers)} objetos para '{query}'.")
                    return offers
                else:
                    status_code = response.status_code if response else "No Response"
                    self._log(f"⚠️ Wallapop API ha devuelto código de estado no-exitoso: {status_code}", level="warning")
            except Exception as e:
                self._log(f"⚠️ Error llamando a la API de Wallapop: {e}", level="warning")
                
        return []

    async def search(self, query: str) -> List[ScrapedOffer]:
        offers: List[ScrapedOffer] = []
        
        # CloudFront blocks GitHub Actions / OCI Datacenter IPs by default.
        # To avoid wasting proxy credits and API calls, we skip Wallapop during scheduled automated daily scans (DAILY_SCAN_RUN) and GitHub Actions.
        # Apify and ScraperAPI are reserved exclusively for manual triggered searches from the admin panel.
        if os.environ.get("DAILY_SCAN_RUN") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
            self._log("⚠️ Wallapop: Detectado entorno automatizado programado (daily_scan / GitHub Actions). Saltando búsqueda para preservar créditos (reservado para llamada manual).")
            return []
            
        # 1. Configuración inteligente de palabras clave
        if query == "auto":
            queries_config = [
                ("masters del universo origins", 4, True),   # (query, scroll_cycles, click_load_more)
                ("masters of the universe origins", 4, True),
                ("motu origins", 4, True)
            ]
        else:
            queries_config = [(query, 8, True)]
            
        self._log(f"🌩️ Wallapop Nexus: Iniciando búsqueda integrada para {len(queries_config)} términos.")
        
        # --- INTENTO 1: API DIRECTA CON IMPERSONACIÓN ---
        api_success = True
        api_offers: List[ScrapedOffer] = []
        max_items = 30 if query == "auto" else 40
        
        for search_query, _, _ in queries_config:
            try:
                res = await self.search_via_api(search_query, max_items=max_items)
                if res:
                    api_offers.extend(res)
                else:
                    # Si la API no retorna nada, consideramos probar con Playwright
                    api_success = False
            except Exception:
                api_success = False
                
        if api_success and api_offers:
            # Deduplicar ofertas
            seen_urls = set()
            unique_offers = []
            for o in api_offers:
                if o.url not in seen_urls:
                    seen_urls.add(o.url)
                    unique_offers.append(o)
            self.items_scraped = len(unique_offers)
            self._log(f"🚀 Wallapop API: Búsqueda completada con éxito. {self.items_scraped} reliquias encontradas sin levantar navegador.")
            return unique_offers

        # --- INTENTO 2: FALLBACK CON PLAYWRIGHT Y PERFIL PERSISTENTE (Solo local) ---
        if os.environ.get("GITHUB_ACTIONS") == "true":
            self._log("⚠️ Wallapop: API directa fallida en GitHub Actions. Saltando fallback de Playwright para evitar bloqueos CloudWAF.")
            seen_urls = set()
            unique_offers = []
            for o in api_offers:
                if o.url not in seen_urls:
                    seen_urls.add(o.url)
                    unique_offers.append(o)
            self.items_scraped = len(unique_offers)
            return unique_offers

        self._log("🌐 Wallapop Fallback: La API directa no ha retornado datos. Levantando navegador Playwright...", level="warning")
        
        # Try direct connection first, fallback to proxy if blocked by WAF and api_key is present
        api_key = os.environ.get("SCRAPERAPI_KEY")
        use_proxy_options = [False]
        if api_key:
            use_proxy_options.append(True)

        for use_proxy in use_proxy_options:
            self.blocked = False
            proxy_config = None
            profile_suffix = "proxy" if use_proxy else "direct"
            user_data_dir = os.path.join(tempfile.gettempdir(), f"playwright_wallapop_profile_{profile_suffix}")
            
            if use_proxy:
                proxy_config = {
                    "server": "http://proxy-server.scraperapi.com:8001",
                    "username": "scraperapi.country_code=es.premium=true",
                    "password": api_key
                }
                self._log("📡 Re-intentando Playwright con proxy de ScraperAPI (Premium ES)...")

            is_headless = True
            if not use_proxy and os.environ.get("GITHUB_ACTIONS") != "true":
                # Ensure we don't launch headed browser in a headless Linux environment (like Docker/WSL without XServer)
                import sys
                if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
                    is_headless = True
                else:
                    is_headless = False

            try:
                self._log(f"🌐 Iniciando navegador Playwright ({profile_suffix}, headless={is_headless})...")
                async with async_playwright() as p:
                    # Lanzar con perfil persistente para mantener cookies
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir,
                        headless=is_headless,
                        proxy=proxy_config,
                        ignore_https_errors=True,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-infobars',
                            '--disable-dev-shm-usage',
                            '--disable-browser-side-navigation',
                            '--disable-gpu'
                        ],
                        viewport={'width': 1280, 'height': 800},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        locale="es-ES"
                    )
                    
                    page = context.pages[0] if context.pages else await context.new_page()
                    
                    await page.add_init_script("""
                        // Ocultar automatización de webdriver
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                        
                        // Ocultar idiomas
                        Object.defineProperty(navigator, 'languages', { get: () => ['es-ES', 'es', 'en'] });
                        
                        // Simular plugins reales
                        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                        
                        // Parchear permisos query
                        const originalQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (parameters) => (
                            parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                        );
                        
                        // Simular objeto chrome
                        window.chrome = { runtime: {} };
                    """)
                    
                    current_ip = "Desconocida"
                    probe_status = "error"
                    environment = "GitHub Actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "Local"
                    resp_code = None
                    details_str = "No details available."

                    try:
                        # Obtener la IP actual
                        await page.goto("https://api.ipify.org?format=json", timeout=15000)
                        ip_text = await page.locator("body").text_content()
                        import json
                        ip_data = json.loads(ip_text.strip())
                        current_ip = ip_data.get("ip", "Desconocida")
                        self._log(f"🔎 IP de origen detectada: {current_ip}")
                    except Exception as e:
                        self._log(f"🔎 IP de origen: No se pudo determinar ({e})")

                    if not use_proxy:
                        try:
                            # Probar acceso a la portada
                            self._log("🏠 Validando estado de conexión con portada de Wallapop...")
                            response = await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                            if response:
                                resp_code = response.status
                            
                            cover_content = await page.content()
                            page_title = await page.title()
                            
                            if "request could not be satisfied" in cover_content.lower() or "403 error" in cover_content.lower() or "request blocked" in cover_content.lower() or ("cloudflare" in cover_content.lower() and ("blocked" in cover_content.lower() or "security" in cover_content.lower())):
                                if not is_headless:
                                    self._log("⚠️ Cloudflare WAF detectado. Por favor, resuelve el Captcha en la ventana del navegador...")
                                    for _ in range(20):
                                        await asyncio.sleep(1)
                                        cover_content = await page.content()
                                        if not ("cloudflare" in cover_content.lower() and ("blocked" in cover_content.lower() or "security" in cover_content.lower())):
                                            self._log("🎉 Captcha resuelto manualmente o redirigido con éxito!")
                                            break
                                    
                                    cover_content = await page.content()
                                    page_title = await page.title()
                                    
                            if "request could not be satisfied" in cover_content.lower() or "403 error" in cover_content.lower() or "request blocked" in cover_content.lower() or ("cloudflare" in cover_content.lower() and ("blocked" in cover_content.lower() or "security" in cover_content.lower())):
                                probe_status = "blocked"
                                details_str = f"Blocked page title: {page_title}. Content starts with: {cover_content[:500]}"
                                self._log(f"🛡️ [PROBE] IP {current_ip} BLOQUEADA por WAF de CloudFront. Abortando.", level="warning")
                                self.blocked = True
                            else:
                                probe_status = "allowed"
                                details_str = f"Successfully loaded Wallapop. Title: {page_title}. Response status: {resp_code}"
                                
                                # Consentimiento de Cookies
                                accept_btn = page.locator("#onetrust-accept-btn-handler").or_(
                                    page.get_by_role("button", name="Aceptar todo")
                                ).or_(
                                    page.locator("button:has-text('Aceptar')")
                                ).first
                                
                                if await accept_btn.is_visible(timeout=5000):
                                    await accept_btn.click()
                                    self._log("🍪 Cookies aceptadas en portada.")
                                await asyncio.sleep(2)
                        except Exception as e:
                            probe_status = "error"
                            details_str = f"Navigation failed: {e}"
                            self._log(f"⚠️ [PROBE] Falló la comprobación de red: {e}", level="warning")
                            self.blocked = True
                    else:
                        probe_status = "proxy_bypass"
                        details_str = "Bypassing probe because proxy is enabled."

                    # Registrar telemetría IP
                    try:
                        from src.infrastructure.database_cloud import SessionCloud
                        from src.domain.models import WallapopIpLogModel
                        with SessionCloud() as db_session:
                            ip_log = WallapopIpLogModel(
                                ip_address=current_ip,
                                status=probe_status,
                                environment=environment,
                                response_code=resp_code,
                                details=details_str
                            )
                            db_session.add(ip_log)
                            db_session.commit()
                    except Exception as db_err:
                        self._log(f"⚠️ No se pudo registrar la auditoría IP: {db_err}", level="warning")

                    if self.blocked:
                        self._log(f"🛡️ [WAF] Cerrando contexto de navegador Playwright ({profile_suffix}) por bloqueo...")
                        await context.close()
                        self._log(f"🛡️ [WAF] Contexto ({profile_suffix}) cerrado. Continuando bucle...")
                        # Si falló la conexión directa y hay una clave proxy disponible, el bucle reintentará con proxy
                        continue
                    
                    try:
                        for search_query, scroll_cycles, click_load_more in queries_config:
                            if self.blocked:
                                break
                                
                            self._log(f"🕵️ Wallapop Browser: Navegando directamente a resultados de '{search_query}'...")
                            
                            try:
                                # Navegar directamente por parámetros de URL (Stealth & Veloz)
                                search_url = f"https://es.wallapop.com/app/search?keywords={search_query}"
                                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                                await asyncio.sleep(2.5)
                                
                                # Manejo cookies en resultados
                                try:
                                    accept_btn = page.locator("#onetrust-accept-btn-handler").or_(
                                        page.get_by_role("button", name="Aceptar todo")
                                    ).or_(
                                        page.locator("button:has-text('Aceptar')")
                                    ).first
                                    if await accept_btn.is_visible(timeout=3000):
                                        await accept_btn.click()
                                        await asyncio.sleep(1.0)
                                except Exception:
                                    pass
                                    
                                # Validar si devolvió un bloqueo de IP
                                content = await page.content()
                                if "request could not be satisfied" in content.lower() or "403 error" in content.lower() or "request blocked" in content.lower():
                                    self._log("🛡️ Bloqueo WAF detectado al cargar los resultados de búsqueda.", level="warning")
                                    self.blocked = True
                                    break
                                
                                # Cargar más
                                if click_load_more:
                                    try:
                                        await page.keyboard.press("End")
                                        await asyncio.sleep(1.0)
                                        load_more_btn = page.get_by_role("button", name="Cargar más").or_(page.locator("button:has-text('Cargar más')")).first
                                        if await load_more_btn.is_visible(timeout=4000):
                                            await load_more_btn.click()
                                            await page.wait_for_load_state("networkidle")
                                            await asyncio.sleep(1.5)
                                    except Exception:
                                        pass
                                        
                                # Scrolls
                                for i in range(scroll_cycles):
                                    await page.mouse.wheel(0, 1500)
                                    await asyncio.sleep(1.0)
                                    
                                # Parsear HTML
                                content = await page.content()
                                soup = BeautifulSoup(content, 'html.parser')
                                cards = soup.select("a[href*='/item/']")
                                
                                query_offers_count = 0
                                for card in cards:
                                    try:
                                        price_node = card.select_one("span[class*='Price'], [class*='price']")
                                        title_node = card.select_one("p[class*='Title'], [class*='title']")
                                        img_node = card.select_one("img")
                                        
                                        if not price_node or not title_node:
                                            continue
                                            
                                        price_text = price_node.get_text(strip=True)
                                        price_val = float(re.sub(r'[^\d.,]', '', price_text).replace(',', '.'))
                                        if price_val <= 0: continue
                                        
                                        title = title_node.get_text(strip=True)
                                        title_lower = title.lower()
                                        junk_keywords = ["camiseta", "t-shirt", "poster", "taza", "mug", "revista", "dvd", "llavero", "keyring", "reproduccion", "repro", "sticker", "pegatina"]
                                        if any(kw in title_lower for kw in junk_keywords):
                                            continue
                                            
                                        href = card.get("href", "")
                                        clean_href = href.split("?")[0]
                                        full_url = clean_href if clean_href.startswith("http") else f"{self.base_url}{clean_href}"
                                        
                                        image_url = img_node.get("src") if img_node else None
                                        
                                        if any(o.url == full_url for o in offers):
                                            continue
                                            
                                        offer = ScrapedOffer(
                                            product_name=title,
                                            price=price_val,
                                            url=full_url,
                                            shop_name=self.shop_name,
                                            image_url=image_url,
                                            source_type="Peer-to-Peer",
                                            sale_type="Fixed_P2P"
                                        )
                                        offers.append(offer)
                                        query_offers_count += 1
                                        
                                    except Exception:
                                        continue
                                        
                                self._log(f"🎁 Wallapop Browser: Halladas {query_offers_count} reliquias para '{search_query}'.")
                                await asyncio.sleep(random.uniform(2.0, 4.0))
                                
                            except Exception as e:
                                self._log(f"⚠️ Error buscando '{search_query}' en navegador: {e}", level="warning")
                                
                    except Exception as e:
                        self._log(f"💥 Error general en Wallapop Playwright Fallback: {e}", level="error")
                        self.errors += 1
                    finally:
                        await context.close()
                    
                    # Deduplicar ofertas y finalizar búsqueda exitosa
                    seen_urls = set()
                    unique_offers = []
                    for o in offers:
                        if o.url not in seen_urls:
                            seen_urls.add(o.url)
                            unique_offers.append(o)
                    self.items_scraped = len(unique_offers)
                    self._log(f"✅ Wallapop Fallback Complete: Halladas {self.items_scraped} reliquias en total.")
                    return unique_offers
                    

            except Exception as e:
                self._log(f"💥 Error general en Wallapop Playwright Fallback: {e}", level="error")
                self.errors += 1

        self.items_scraped = len(offers)
        self._log(f"✅ Wallapop Fallback Complete: Halladas {self.items_scraped} reliquias en total.")
        return offers

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    async def test():
        scraper = WallapopScraper()
        results = await scraper.search("masters of the universe origins")
        print(f"\n--- RESULTADOS FINALES ---")
        print(f"Total: {len(results)}")
        for r in results[:10]:
            print(f"- {r.product_name}: {r.price}€ -> {r.url}")
            
    asyncio.run(test())
