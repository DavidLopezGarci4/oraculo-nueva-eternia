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
        self.search_url = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"
        
        # --- CONFIGURACIÓN DE OPCIONES DE BYPASS ---
        self.use_managed_api = False  # Cambiar a True para activar la OPCIÓN 2 (ScraperAPI Premium)

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        """
        Incursión para extraer reliquias MOTU de Smyths Toys Alemania.
        """
        self._log(f"🔎 Iniciando búsqueda en Smyths Toys para: {query}")
        
        if self.use_managed_api:
            return await self._search_option_2(query)
        else:
            return await self._search_option_1(query)

    async def _search_option_1(self, query: str) -> List[ScrapedOffer]:
        """
        OPCIÓN 1: Playwright con perfil persistente, Chrome local, precarga de cookies de home y referer.
        """
        from playwright.async_api import async_playwright
        
        self._log("🛡️ Ejecutando OPCIÓN 1: Playwright con perfil persistente y referer home")
        products: List[ScrapedOffer] = []
        seen_urls = set()
        user_agent = random.choice(self.USER_AGENTS)
        
        # Crear directorio temporal para el perfil de usuario persistente
        user_data_dir = tempfile.mkdtemp(prefix="playwright_smyths_profile_")
        
        async with async_playwright() as p:
            browser_context = None
            try:
                # Lanzar perfil persistente intentando usar el canal real de Google Chrome (ideal para Windows)
                try:
                    self._log("🌐 Lanzando Google Chrome (Canal Persistente)...")
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        headless=True,
                        channel="chrome",
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--no-sandbox',
                            '--disable-web-security',
                            '--disable-features=IsolateOrigins,site-per-process',
                        ],
                        viewport={'width': 1366, 'height': 768},
                        locale='de-DE',
                        timezone_id='Europe/Berlin',
                        user_agent=user_agent
                    )
                except Exception as e:
                    self._log(f"⚠️ No se pudo lanzar canal 'chrome' ({e}). Usando Chromium por defecto...")
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        headless=True,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--no-sandbox',
                            '--disable-web-security',
                            '--disable-features=IsolateOrigins,site-per-process',
                        ],
                        viewport={'width': 1366, 'height': 768},
                        locale='de-DE',
                        timezone_id='Europe/Berlin',
                        user_agent=user_agent
                    )
                
                await browser_context.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
                
                # --- INYECCIÓN PROFUNDA DE ANTIDETECT (Evita la firma automatizada) ---
                await page.add_init_script("delete navigator.__proto__.webdriver")
                await page.add_init_script("""
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['de-DE', 'de', 'en-US', 'en']
                    });
                    
                    const mockPlugin = (name, filename, description) => {
                        const plugin = Object.create(Plugin.prototype);
                        Object.defineProperties(plugin, {
                            name: { value: name, enumerable: true },
                            filename: { value: filename, enumerable: true },
                            description: { value: description, enumerable: true },
                        });
                        return plugin;
                    };
                    const pluginsList = [
                        mockPlugin('PDF Viewer', 'internal-pdf-viewer', 'Portable Document Format'),
                        mockPlugin('Chrome PDF Viewer', 'mhjfbgojcjbhgoocpbhnapeenohidgkm', 'Portable Document Format')
                    ];
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => pluginsList,
                        enumerable: true,
                        configurable: true
                    });
                """)
                
                # Paso 1: Aterrizaje en la Home para establecer cookies de sesión
                self._log("🏠 Aterrizando en la página de inicio para inicializar cookies...")
                await page.goto("https://www.smythstoys.com/de/de-de", wait_until="commit", timeout=45000)
                
                # Monitorear si aparece desafío e intentar darle tiempo para resolver
                for i in range(10):
                    await asyncio.sleep(1)
                    try:
                        title = await page.title()
                        if title and "Pardon Our Interruption" not in title:
                            break
                    except Exception:
                        pass
                
                # Espera aleatoria para asentamiento de cookies
                await asyncio.sleep(random.uniform(2.5, 4.5))
                
                # Paso 2: Navegación a la categoría MOTU especificando referer de la home
                self._log(f"🧭 Navegando a la categoría con referer de la home...")
                resp = await page.goto(
                    self.search_url,
                    referer="https://www.smythstoys.com/de/de-de",
                    wait_until="commit",
                    timeout=60000
                )
                
                # Esperar resolución de reto si existiera en la navegación secundaria
                for i in range(10):
                    await asyncio.sleep(1)
                    try:
                        title = await page.title()
                        if title and "Pardon Our Interruption" not in title:
                            break
                    except Exception:
                        pass
                
                # --- EMULACIÓN DE COMPORTAMIENTO HUMANO ---
                self._log("🖱️ Simulando lectura de usuario (scroll y movimientos)")
                for _ in range(3):
                    scroll_y = random.randint(350, 700)
                    await page.mouse.wheel(0, scroll_y)
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                    
                # Volver a subir levemente para simular comportamiento orgánico
                await page.mouse.wheel(0, -random.randint(100, 250))
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                body_text = soup.body.get_text() if soup.body else ""
                
                # Detección defensiva de bloqueo
                if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower() or "incident id" in html.lower():
                    self._log("⚠️ Bloqueo de Imperva (Incapsula) detectado en la opción local.", level="warning")
                    self.blocked = True
                    return []
                
                # Parsear contenido
                products = self._parse_html(soup, seen_urls)
                
            except Exception as e:
                self._log(f"❌ Error en Playwright (Opción 1): {e}", level="error")
                self.errors += 1
            finally:
                if browser_context:
                    await browser_context.close()
                # Eliminar carpeta del perfil de usuario temporal
                try:
                    shutil.rmtree(user_data_dir)
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
                
            # Construir URL absoluta
            if not href.startswith("http"):
                full_url = f"https://www.smythstoys.com{href}"
            else:
                full_url = href
                
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            # 1. Nombre del Producto (Traversing headings/links)
            name = link_tag.get_text(strip=True)
            if not name or len(name) < 5:
                title_el = link_tag.select_one("h2, h3, p, span")
                if title_el:
                    name = title_el.get_text(strip=True)
            
            # Buscar el contenedor del producto (card/grid item) subiendo hasta 4 niveles
            parent = link_tag.parent
            card_container = None
            for _ in range(4):
                if not parent:
                    break
                cls_str = " ".join(parent.get("class", []))
                if any(w in cls_str.lower() for w in ["product", "item", "tile", "grid", "card"]):
                    card_container = parent
                    break
                parent = parent.parent
                
            if not card_container:
                card_container = link_tag.parent
                
            # Si el nombre sigue vacío, buscar una cabecera en el contenedor
            if not name or len(name) < 5:
                heading = card_container.select_one("h2, h3, h4, .title, .name")
                if heading:
                    name = heading.get_text(strip=True)
                    
            if not name or len(name) < 5:
                continue
                
            # Limpieza del título
            name = name.replace("\n", " ").strip()
            
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
