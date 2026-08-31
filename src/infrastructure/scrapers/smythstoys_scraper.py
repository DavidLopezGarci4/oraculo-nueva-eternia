from typing import List, Optional
import asyncio
import logging
import random
import re
import os
import shutil
import tempfile
import urllib.parse
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer

logger = logging.getLogger(__name__)

class SmythsToysScraper(BaseScraper):
    """
    Scraper para Smyths Toys (Alemania - DE).
    Implementa dos opciones de evasión de WAF (Imperva/Incapsula):
    
    - OPCIÓN 1 (Activa por defecto): Playwright Persistent Context (Chrome Channel) con 
      inyección profunda de antidetect, aterrizaje previo en la home para cookies y referer simulación.
    - OPCIÓN 2 (Estructurada como fallback): API gestionada premium (ScraperAPI con render y premium).
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    def __init__(self):
        super().__init__(
            shop_name="SmythsToys",
            base_url="https://www.smythstoys.com"
        )
        self.category_url = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt+desc"
        self.search_url = self.category_url
        self.keywords_de = "masters of the universe figuren und sets"
        
        # --- CONFIGURACIÓN DE OPCIONES DE BYPASS ---
        self.use_managed_api = False  # Si es True, fuerza el uso de ScraperAPI

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        """
        Incursión para extraer reliquias MOTU de Smyths Toys Alemania.
        Cascada Zero-Cost:
        1. Nivel 1 (Gratis): Infiltración rápida curl_cffi con TLS Chrome 124 a categoría / buscador.
        2. Nivel 2 (Gratis): Playwright Headless con Antidetect e inicialización de cookies.
        3. Nivel 3 (Reserva): ScraperAPI Premium solo si los métodos gratuitos fallan.
        """
        self._log(f"🔎 Iniciando búsqueda en Smyths Toys para: {query}")
        self.blocked = False
        
        # Nivel 1: Fast Infiltration directa con curl_cffi (Gratis)
        self._log("⚡ SmythsToys [Nivel 1 Gratis]: Probando infiltración directa con curl-cffi...")
        offers = await self._fast_infiltration(query)
        if offers and not self.blocked:
            self._log(f"🎉 SmythsToys [Nivel 1 Gratis]: ¡Éxito! Encontradas {len(offers)} ofertas.")
            return offers

        # Nivel 2: Playwright Headless con antidetect profundo (Gratis)
        self._log("🛡️ SmythsToys [Nivel 2 Gratis]: Infiltración rápida bloqueada/vacía. Escalamiento a Playwright Antidetect...", level="warning")
        self.blocked = False
        offers = await self._search_option_1(query)
        if offers and not self.blocked:
            return offers

        # Nivel 3: ScraperAPI Premium (Solo si hay clave configurada)
        if os.environ.get("SCRAPERAPI_KEY"):
            self._log("📡 SmythsToys [Nivel 3 Reserva]: Activando ScraperAPI de rescate...", level="warning")
            self.blocked = False
            offers = await self._search_option_2(query)

        return offers

    async def _fast_infiltration(self, query: str) -> List[ScrapedOffer]:
        """Infiltración ultrarrápida gratuita vía curl_cffi."""
        target_url = self.category_url
        if query and query.lower() != "auto":
            encoded_query = urllib.parse.quote_plus(query)
            target_url = f"https://www.smythstoys.com/de/de-de/search/?text={encoded_query}"

        offers: List[ScrapedOffer] = []
        try:
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.smythstoys.com/de/de-de",
                "Upgrade-Insecure-Requests": "1"
            }
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.get(target_url, headers=headers, timeout=20)
                if resp.status_code == 200:
                    body_text = resp.text.lower()
                    if "pardon our interruption" in body_text or "incapsula" in body_text or "incident id" in body_text:
                        self._log("🛡️ SmythsToys: Desafío Imperva detectado en curl_cffi.", level="debug")
                        self.blocked = True
                        return []
                    soup = BeautifulSoup(resp.text, "html.parser")
                    offers = self._parse_html(soup, set())
                else:
                    self._log(f"⚠️ SmythsToys: HTTP {resp.status_code} en curl_cffi", level="debug")
        except Exception as e:
            self._log(f"⚠️ SmythsToys: Error en fast infiltration: {e}", level="debug")
            
        return offers

    async def _search_option_1(self, query: str) -> List[ScrapedOffer]:
        """
        OPCIÓN 1: Playwright con perfil persistente, Chrome local, inyección profunda antidetect y resolución WAF.
        """
        from playwright.async_api import async_playwright
        
        # Determinar si se ejecuta de forma oculta o visible.
        # En entornos locales y Nexus, usamos modo visible con canal Chrome para máxima evasión de WAF.
        is_headless = False
        if os.environ.get("DAILY_SCAN_RUN") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
            is_headless = True
            self._log("🛡️ Ejecutando OPCIÓN 1: Playwright con perfil persistente en modo headless")
        else:
            self._log("👁️ Modo visible (headful) activo para incursión de alta confianza (anti-Imperva).")
            
        products: List[ScrapedOffer] = []
        seen_urls = set()
        
        # 1. Intento de conexión CDP asistida (si el usuario tiene su Chrome de depuración abierto en puerto 9222)
        if not is_headless:
            try:
                import urllib.request
                urllib.request.urlopen("http://localhost:9222/json/version", timeout=0.5)
                self._log("🔌 Puerto de depuracion 9222 abierto detectado. Conectando via CDP...")
                
                async with async_playwright() as p:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                    target_page = None
                    for context in browser.contexts:
                        for page in context.pages:
                            if "smythstoys.com" in page.url:
                                target_page = page
                                break
                        if target_page:
                            break
                            
                    if not target_page:
                        # Abrir pestaña en el navegador del usuario directamente vía CDP
                        self._log("🧭 Abriendo pestaña en sesión activa de Chrome para Smyths Toys...")
                        context = browser.contexts[0] if browser.contexts else await browser.new_context()
                        target_page = await context.new_page()
                        await target_page.goto(self.search_url, wait_until="domcontentloaded", timeout=45000)
                        await asyncio.sleep(3)

                    self._log(f"🎯 Pestaña activa de Smyths Toys obtenida: {target_page.url}")
                    html = await target_page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    products = self._parse_html(soup, seen_urls)
                    if products:
                        self._log(f"✅ Extracción completada exitosamente vía CDP. Encontrados {len(products)} artículos.")
                        return products
            except Exception as e_cdp:
                self._log(f"ℹ️ CDP no utilizado ({e_cdp}). Continuando con canal autónomo...")
                
        # Perfil persistente en el proyecto para conservar cookies de sesión de Imperva
        user_data_dir = os.path.abspath(os.path.join(os.getcwd(), "data", "smyths_chrome_profile"))
        os.makedirs(user_data_dir, exist_ok=True)
        
        target_url = self.category_url
        if query and query.lower() not in ["auto", "completo", "full", "deep", "exhaustivo"]:
            encoded_query = urllib.parse.quote_plus(query)
            target_url = f"https://www.smythstoys.com/de/de-de/search/?text={encoded_query}"
        
        async with async_playwright() as p:
            browser_context = None
            try:
                launch_args = [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--window-size=1366,768"
                ]
                
                try:
                    self._log("🌐 Lanzando Google Chrome (Canal Persistente con Antidetect)...")
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        headless=is_headless,
                        channel="chrome",
                        ignore_default_args=["--enable-automation"],
                        args=launch_args,
                        viewport={"width": 1366, "height": 768},
                        locale="de-DE",
                        timezone_id="Europe/Berlin"
                    )
                except Exception as e:
                    self._log(f"⚠️ Fallback a Chromium por defecto ({e})...")
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        headless=is_headless,
                        ignore_default_args=["--enable-automation"],
                        args=launch_args,
                        viewport={"width": 1366, "height": 768},
                        locale="de-DE",
                        timezone_id="Europe/Berlin"
                    )
                
                page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
                
                # Inyección de stealth para ocultar automatización
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {} };
                """)
                
                self._log(f"🧭 Navegando a catálogo de Smyths Toys...")
                try:
                    await page.goto(target_url, timeout=45000)
                except Exception as nav_e:
                    self._log(f"ℹ️ Conexión inicial: {nav_e}", level="debug")
                
                # Esperar resolución de reto / recarga automática de Imperva
                for i in range(20):
                    await asyncio.sleep(1.5)
                    try:
                        title = await page.title()
                        if title and "Pardon Our Interruption" not in title and len(title) > 0:
                            self._log(f"✅ Acceso concedido a Smyths Toys: '{title[:55]}...'")
                            break
                    except Exception:
                        # Recarga de contexto por redirección de WAF en curso
                        pass
                
                # Emulación de scroll humano para cargar elementos
                self._log("🖱️ Simulando lectura de usuario y scroll orgánico...")
                for _ in range(3):
                    await page.mouse.wheel(0, random.randint(400, 750))
                    await asyncio.sleep(random.uniform(0.8, 1.6))
                    
                await asyncio.sleep(2)
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                body_text = soup.body.get_text() if soup.body else ""
                
                products = self._parse_html(soup, seen_urls)
                
                if len(products) == 0 and ("pardon our interruption" in body_text.lower() or "incident id" in body_text.lower()):
                    self._log("⚠️ Bloqueo de Imperva persistente en este intento.", level="warning")
                    self.blocked = True
                    return []
                    
                if products:
                    self._log(f"🎉 SmythsToys [Playwright]: ¡Éxito! Extraídas {len(products)} reliquias.")
                
            except Exception as e:
                self._log(f"❌ Error en Playwright (Opción 1): {e}", level="error")
                self.errors += 1
            finally:
                if browser_context:
                    try:
                        await browser_context.close()
                    except Exception:
                        pass
                
        return products

    async def _search_option_2(self, query: str) -> List[ScrapedOffer]:
        """
        OPCIÓN 2: API Gestionada Premium (ScraperAPI con premium=true y render=true).
        """
        self._log("🌐 Ejecutando OPCIÓN 2: Ruta gestionada a través de ScraperAPI Premium")
        import os
        scraperapi_key = os.environ.get("SCRAPERAPI_KEY")
        if not scraperapi_key:
            self._log("❌ No se encontró SCRAPERAPI_KEY en variables de entorno. Abortando.", level="error")
            self.errors += 1
            return []
            
        products: List[ScrapedOffer] = []
        seen_urls = set()
        
        # Parámetros de evasión de ScraperAPI
        params_sa = {
            "api_key": scraperapi_key,
            "url": self.search_url,
            "country_code": "de",
            "premium": "true",
            "render": "true"
        }
        query_string = urllib.parse.urlencode(params_sa)
        api_url = f"http://api.scraperapi.com?{query_string}"
        
        try:
            self._log(f"📡 Realizando solicitud a ScraperAPI Premium para Smyths Toys...")
            async with AsyncSession() as session:
                resp = await session.get(api_url, timeout=90)
                self._log(f"📡 Respuesta de ScraperAPI: {resp.status_code}")
                
                if resp.status_code == 403:
                    self._log("⚠️ ScraperAPI: Créditos agotados o clave inválida (HTTP 403).", level="warning")
                    self.blocked = True
                    return []
                    
                if resp.status_code != 200:
                    self._log(f"❌ Fallo en ScraperAPI con código: {resp.status_code}", level="error")
                    self.errors += 1
                    return []
                    
                soup = BeautifulSoup(resp.text, "html.parser")
                body_text = soup.body.get_text() if soup.body else ""
                
                if "pardon our interruption" in body_text.lower() or "incapsula" in resp.text.lower():
                    self._log("❌ Bloqueado por Imperva incluso mediante ScraperAPI.", level="error")
                    self.blocked = True
                    return []
                    
                products = self._parse_html(soup, seen_urls)
                
        except Exception as e:
            self._log(f"❌ Error al consultar ScraperAPI (Opción 2): {e}", level="error")
            self.errors += 1
            
        return products

    def _parse_html(self, soup: BeautifulSoup, seen_urls: set) -> List[ScrapedOffer]:
        """
        Algoritmo de parseo tolerante a fallos y auto-curable de Smyths Toys.
        """
        parsed_offers: List[ScrapedOffer] = []
        
        # Extrae todos los enlaces que contengan /p/ (patrón característico de productos)
        product_links = soup.select("a[href*='/p/']")
        self._log(f"🔎 Enlaces de productos encontrados en el DOM: {len(product_links)}")
        
        for link_tag in product_links:
            href = link_tag.get("href")
            if not href:
                continue
                
            # Evitar enlaces promocionales o de navegación en cabeceras/menús/pie de página
            is_navigation_or_promo = False
            p_check = link_tag.parent
            for _ in range(8):
                if not p_check:
                    break
                cls_list = p_check.get("class", [])
                cls_str_check = " ".join(cls_list).lower() if isinstance(cls_list, list) else str(cls_list).lower()
                id_str_check = str(p_check.get("id", "")).lower()
                tag_name = p_check.name.lower()
                
                if any(w in cls_str_check or w in id_str_check for w in ["menu", "navigation", "header", "nav", "promo", "footer", "mega"]):
                    is_navigation_or_promo = True
                    break
                if tag_name in ["header", "nav", "footer"]:
                    is_navigation_or_promo = True
                    break
                p_check = p_check.parent
                
            if is_navigation_or_promo:
                continue
                
            # Construir URL absoluta
            if not href.startswith("http"):
                full_url = f"https://www.smythstoys.com{href}"
            else:
                full_url = href
                
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            # Buscar el contenedor del producto (card/grid item) subiendo hasta 4 niveles
            parent = link_tag.parent
            card_container = None
            for _ in range(4):
                if not parent:
                    break
                cls_str = " ".join(parent.get("class", []))
                # Evitamos subir hasta contenedores anchos generales de rejilla (ej. grid, row, container, grow, pb-8)
                if any(w in cls_str.lower() for w in ["grid", "list-container", "row", "container", "grow", "pb-8"]):
                    break
                if any(w in cls_str.lower() for w in ["product", "item", "tile", "card", "rounded-lg", "border-grey-200"]):
                    card_container = parent
                    break
                card_container = parent
                parent = parent.parent
                
            if not card_container:
                card_container = link_tag.parent
                
            # 1. Nombre del Producto (Intentar primero con alt de la imagen o tags de título para evitar precios acoplados)
            name = ""
            img_tag = card_container.select_one("img")
            if img_tag and img_tag.get("alt"):
                name = img_tag.get("alt").strip()
                
            if not name or len(name) < 5:
                # Buscar encabezados dentro del contenedor
                title_el = card_container.select_one("h2, h3, h4, .title, .name")
                if title_el:
                    name = title_el.get_text(strip=True)
                    
            if not name or len(name) < 5:
                name = link_tag.get_text(strip=True)
                
            if not name or len(name) < 5:
                continue
                
            # Limpieza y saneamiento del título del producto
            name = name.replace("\n", " ").strip()
            
            # Remover precios residuales pegados al final del texto (ej: 21,99€, 17.99 EUR, 99.99€, etc.)
            name = re.sub(r'\d+[.,]\d{2}\s*(?:€|EUR|\$)', '', name)
            
            # Remover textos promocionales alemanes colados (ej: 27% OFF, 27%, Vorheriger Verkaufspreis)
            name = re.sub(r'(?i)\d+%\s*off\b', '', name)
            name = re.sub(r'(?i)\d+%\b', '', name)
            name = re.sub(r'(?i)\bvorheriger\s+verkaufspreis\b', '', name)
            
            # Remover palabras "Exklusiv" y "Masters of the Universe" para facilitar la asociación en la Fortaleza
            # (Limpieza insensiva a mayúsculas/minúsculas y que actúe incluso si están unidas como "ExklusivMasters")
            name = re.sub(r'(?i)exklusiv', '', name)
            name = re.sub(r'(?i)masters\s+of\s+the\s+universe', '', name)
            
            # Limpiar espacios múltiples y caracteres sueltos residuales resultantes
            name = re.sub(r'\s+', ' ', name).strip()
            name = name.strip("-,. ")
            
            # 2. Búsqueda de Precio
            price_val = 0.0
            price_tag = card_container.select_one(".price, [class*='price'], [class*='Price'], [itemprop='price']")
            if price_tag:
                price_val = self._normalize_price(price_tag.get_text(strip=True))
            else:
                # Fallback mediante Regex de precios con moneda común (€, $)
                txt = card_container.get_text()
                price_match = re.search(r'(\d+[.,]\d{2})\s*[€$]', txt)
                if price_match:
                    price_val = self._normalize_price(price_match.group(1))
                    
            # 3. Búsqueda de Imagen
            img_url = None
            img_tag = card_container.select_one("img")
            if img_tag:
                img_url = img_tag.get("src") or img_tag.get("data-src")
                if img_url and img_url.startswith("/"):
                    img_url = f"https://www.smythstoys.com{img_url}"
                    
            # 4. Estado de Disponibilidad
            is_avl = True
            txt_lower = card_container.get_text().lower()
            # Términos alemanes característicos de "agotado" o "preventas largas/bloqueadas"
            if any(term in txt_lower for term in ["nicht lieferbar", "ausverkauft", "vorübergehend nicht auf lager", "vorbestellung"]):
                is_avl = False
                
            parsed_offers.append(ScrapedOffer(
                product_name=name,
                price=price_val if price_val > 0 else 19.99,
                currency="EUR",
                url=full_url,
                shop_name="SmythsToys",
                image_url=img_url,
                is_available=is_avl
            ))
            self.items_scraped += 1
            
        self._log(f"✅ Extracción completada para Smyths Toys. Productos parseados: {len(parsed_offers)}")
        return parsed_offers
