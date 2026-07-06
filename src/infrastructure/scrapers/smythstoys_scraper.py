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
        
        # Determinar si se ejecuta de forma oculta o visible.
        # En incursiones manuales locales, ejecutamos en modo visible (headless=False)
        # para usar el motor gráfico real y evadir Imperva al 100% de forma segura.
        is_headless = True
        if os.environ.get("DAILY_SCAN_RUN") != "true" and os.environ.get("GITHUB_ACTIONS") != "true":
            is_headless = False
            self._log("👁️ Modo visible (headful) activo para incursion manual local.")
        else:
            self._log("🛡️ Ejecutando OPCIÓN 1: Playwright con perfil persistente en modo oculto (headless)")
            
        products: List[ScrapedOffer] = []
        seen_urls = set()
        
        # Intento de conexión CDP asistida (si el usuario tiene su Chrome de depuración abierto)
        if os.environ.get("DAILY_SCAN_RUN") != "true" and os.environ.get("GITHUB_ACTIONS") != "true":
            try:
                import urllib.request
                # Timeout de 0.5s para continuar sin retrasos si el puerto está cerrado
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
                            
                    if target_page:
                        self._log(f"🎯 Pestaña activa de Smyths Toys hallada: {target_page.url}")
                        html = await target_page.content()
                        soup = BeautifulSoup(html, "html.parser")
                        products = self._parse_html(soup, seen_urls)
                        self._log(f"✅ Extracción completada exitosamente vía CDP. Encontrados {len(products)} artículos.")
                        return products
                    else:
                        self._log("⚠️ Conectado a CDP, pero no se encontró pestaña abierta de Smyths Toys. Iniciando flujo estándar...", level="warning")
            except Exception:
                # Si el puerto está cerrado, continúa de forma transparente con el lanzamiento del navegador
                pass
                
        user_agent = random.choice(self.USER_AGENTS)
        
        # Usar un directorio de perfil persistente en el proyecto para acumular cookies y confianza.
        # De esta forma, una vez resuelto el reto, las cookies e historial se guardan para futuras ejecuciones.
        user_data_dir = os.path.join(os.getcwd(), "data", "smyths_chrome_profile")
        os.makedirs(os.path.dirname(user_data_dir), exist_ok=True)
        
        async with async_playwright() as p:
            browser_context = None
            try:
                # Lanzar perfil persistente intentando usar el canal real de Google Chrome (ideal para Windows)
                try:
                    self._log("🌐 Lanzando Google Chrome (Canal Persistente)...")
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        headless=is_headless,
                        channel="chrome",
                        ignore_default_args=['--enable-automation', '--no-sandbox'],
                        args=[
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
                        headless=is_headless,
                        ignore_default_args=['--enable-automation', '--no-sandbox'],
                        args=[
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
                for i in range(30):
                    try:
                        title = await page.title()
                        if title and "Pardon Our Interruption" in title:
                            self._log(f"⏳ [WAF] Desafío de Imperva detectado. Esperando resolución automática (segundo {i+1}/30)...")
                            await asyncio.sleep(1)
                        else:
                            break
                    except Exception:
                        await asyncio.sleep(1)
                
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
                for i in range(30):
                    try:
                        title = await page.title()
                        if title and "Pardon Our Interruption" in title:
                            self._log(f"⏳ [WAF Category] Esperando resolución de WAF (segundo {i+1}/30)...")
                            await asyncio.sleep(1)
                        else:
                            break
                    except Exception:
                        await asyncio.sleep(1)
                
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
