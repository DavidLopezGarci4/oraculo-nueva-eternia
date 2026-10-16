from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
import random
import re
import os
import shutil
import socket
import subprocess
import tempfile
import urllib.parse
import urllib.request
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer
from src.infrastructure.scrapers.pipeline import check_is_vintage

logger = logging.getLogger(__name__)


class SmythsToysScraper(BaseScraper):
    """
    Scraper para Smyths Toys (Alemania - DE).
    Implementa el Motor REA/CDP (Coste 0 / 0 Tokens):
    - Acuña la cookie `reese84` de Imperva lanzando Chrome nativo off-screen (o bajo Xvfb en CI)
      y leyendo `Storage.getCookies` desde el WebSocket CDP de nivel navegador (`/json/version`)
      SIN inyectar `Runtime.enable` (indetectable por Imperva).
    - Reutiliza las cookies en `curl_cffi(impersonate="chrome124")` contra `&page=2` y extrae el
      payload SSR completo de Nuxt 3 (`<script id="__NUXT_DATA__">`, 75 productos acumulados).
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]

    DEFAULT_MASTERS_SEARCH_URL = (
        "https://www.smythstoys.com/de/de-de/search"
        "?text=MASTERS&brands=%5B%22Mattel%22%2C%22WWE%22%5D&page=2"
    )

    def __init__(self):
        super().__init__(
            shop_name="SmythsToys",
            base_url="https://www.smythstoys.com",
        )
        self.category_url = self.DEFAULT_MASTERS_SEARCH_URL
        self.search_url = self.DEFAULT_MASTERS_SEARCH_URL
        self.keywords_de = "masters of the universe figuren und sets"
        self.use_managed_api = False

    def _resolve_target_url(self, query: str) -> str:
        if not query or query.lower() in ["auto", "completo", "full", "deep", "exhaustivo", "masters", "motu", "origins"]:
            return self.search_url
        encoded_query = urllib.parse.quote_plus(query)
        return f"https://www.smythstoys.com/de/de-de/search?text={encoded_query}&page=2"

    def _get_proxy_url(self) -> Optional[str]:
        return (
            os.environ.get("SMYTHS_PROXY")
            or os.environ.get("WARP_PROXY")
            or os.environ.get("ALL_PROXY")
            or None
        )

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        """
        Cascada Zero-Cost (0 tokens de Apify):
        1. Nivel 1 (Gratis): Infiltración rápida curl_cffi con TLS Chrome 124 y parser __NUXT_DATA__.
        2. Nivel 2 (Gratis): Motor REA/CDP (Chrome nativo sin Runtime.enable + Storage.getCookies + curl_cffi).
        3. Nivel 3 (Reserva): ScraperAPI si está configurado en el entorno.
        """
        self._log(f"🔎 Iniciando búsqueda en Smyths Toys para: {query}")
        self.blocked = False

        # Nivel 1: Fast Infiltration directa con curl_cffi
        self._log("⚡ SmythsToys [Nivel 1 Gratis]: Probando infiltración directa con curl-cffi...")
        offers = await self._fast_infiltration(query)
        if offers and not self.blocked:
            self._log(f"🎉 SmythsToys [Nivel 1 Gratis]: ¡Éxito! Encontradas {len(offers)} ofertas.")
            return offers

        # Nivel 2: Motor REA/CDP (Cookie Minter sin Runtime.enable + __NUXT_DATA__)
        self._log(
            "🛡️ SmythsToys [Nivel 2 REA/CDP]: Acuñando sesión Imperva (reese84) vía CDP de navegador...",
            level="warning",
        )
        self.blocked = False
        offers = await self._search_rea_cdp(query)
        if offers and not self.blocked:
            return offers

        # Nivel 3: ScraperAPI Premium (solo si hay clave configurada)
        if os.environ.get("SCRAPERAPI_KEY"):
            self._log("📡 SmythsToys [Nivel 3 Reserva]: Activando ScraperAPI de rescate...", level="warning")
            self.blocked = False
            offers = await self._search_option_2(query)

        return offers

    async def _fast_infiltration(self, query: str, cookies: Optional[Dict[str, str]] = None) -> List[ScrapedOffer]:
        """Infiltración ultrarrápida vía curl_cffi y extracción de __NUXT_DATA__."""
        target_url = self._resolve_target_url(query)
        proxy_url = self._get_proxy_url()
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

        offers: List[ScrapedOffer] = []
        try:
            headers = {
                "User-Agent": self.USER_AGENTS[0],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.smythstoys.com/de/de-de/",
                "Upgrade-Insecure-Requests": "1",
            }
            async with AsyncSession(impersonate="chrome124", proxies=proxies) as session:
                resp = await session.get(target_url, headers=headers, cookies=cookies, timeout=25)
                if resp.status_code == 200:
                    body_lower = resp.text.lower()
                    if (
                        len(resp.text) < 25000
                        and ("pardon our interruption" in body_lower or "incapsula" in body_lower or "reese84" in body_lower)
                    ):
                        self._log("🛡️ SmythsToys: Desafío Imperva detectado en curl_cffi.", level="debug")
                        self.blocked = True
                        return []
                    offers = self._extract_offers_from_html(resp.text, set())
                else:
                    self._log(f"⚠️ SmythsToys: HTTP {resp.status_code} en curl_cffi", level="debug")
                    if resp.status_code in (403, 429, 503):
                        self.blocked = True
        except Exception as e:
            self._log(f"⚠️ SmythsToys: Error en fast infiltration: {e}", level="debug")

        return offers

    @staticmethod
    def _find_chrome_executable() -> Optional[str]:
        env_bin = os.environ.get("CHROME_BIN") or os.environ.get("GOOGLE_CHROME_BIN")
        if env_bin and os.path.exists(env_bin):
            return env_bin

        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path

        for cmd in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium", "chrome"):
            found = shutil.which(cmd)
            if found:
                return found
        return None

    async def _fetch_browser_cookies_via_ws(self, ws_url: str) -> Dict[str, str]:
        import websockets

        async with websockets.connect(ws_url, max_size=10_000_000) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Storage.getCookies"}))
            raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
            msg = json.loads(raw)
            cookies_list = msg.get("result", {}).get("cookies", [])
            return {
                c["name"]: c["value"]
                for c in cookies_list
                if "smythstoys" in c.get("domain", "") and c.get("name") and c.get("value")
            }

    async def _mint_imperva_cookies_cdp(self, target_url: str) -> Dict[str, str]:
        """
        Acuña cookies válidas de Imperva (`reese84`) sin usar Playwright ni `Runtime.enable`.
        1. Si el puerto 9222 está activo con cookies de Smyths, las reutiliza al instante.
        2. Si no, lanza un subproceso efímero de Chrome en modo no-headless off-screen
           (o sobre Xvfb en GitHub Actions) y consulta `Storage.getCookies` en `/json/version`.
        """
        # 1. Intentar reutilizar sesión CDP activa en 9222 si existe
        try:
            with urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=0.6) as resp:
                v_info = json.loads(resp.read().decode())
            ws_9222 = v_info.get("webSocketDebuggerUrl")
            if ws_9222:
                cookies_9222 = await self._fetch_browser_cookies_via_ws(ws_9222)
                if "reese84" in cookies_9222:
                    self._log("🔌 Cookie Imperva `reese84` recuperada de sesión Chrome activa (puerto 9222).")
                    return cookies_9222
        except Exception:
            pass

        chrome_bin = self._find_chrome_executable()
        if not chrome_bin:
            self._log("⚠️ No se encontró ejecutable de Google Chrome/Chromium para el Motor REA/CDP.", level="warning")
            return {}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            debug_port = s.getsockname()[1]

        tmp_profile = tempfile.mkdtemp(prefix="smyths_rea_cdp_")
        proxy_url = self._get_proxy_url()

        cmd = [
            chrome_bin,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={tmp_profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-position=-32000,-32000",
            "--window-size=1366,768",
            "--lang=de-DE",
        ]
        if proxy_url:
            cmd.append(f"--proxy-server={proxy_url}")
        cmd.append(target_url)

        proc = None
        minted_cookies: Dict[str, str] = {}
        try:
            self._log(f"🌐 Lanzando Chrome nativo off-screen (puerto {debug_port}) para acuñar token reese84...")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            ws_url = None
            for _ in range(15):
                await asyncio.sleep(0.5)
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json/version", timeout=1.0) as resp:
                        v_info = json.loads(resp.read().decode())
                    ws_url = v_info.get("webSocketDebuggerUrl")
                    if ws_url:
                        break
                except Exception:
                    continue

            if not ws_url:
                self._log("⚠️ No se pudo conectar al endpoint /json/version de Chrome.", level="warning")
                return {}

            for attempt in range(8):
                await asyncio.sleep(2.0)
                try:
                    minted_cookies = await self._fetch_browser_cookies_via_ws(ws_url)
                    if "reese84" in minted_cookies and len(minted_cookies["reese84"]) > 100:
                        self._log(
                            f"✅ Cookie `reese84` acuñada con éxito en intento {attempt + 1} "
                            f"({len(minted_cookies)} cookies de sesión)."
                        )
                        break
                except Exception:
                    continue
        except Exception as e:
            self._log(f"⚠️ Error en Motor REA/CDP: {e}", level="warning")
        finally:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=4)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            shutil.rmtree(tmp_profile, ignore_errors=True)

        return minted_cookies

    async def _search_rea_cdp(self, query: str) -> List[ScrapedOffer]:
        """
        Ejecuta el Motor REA/CDP: acuña cookies de Imperva sin Playwright `Runtime.enable`
        y descarga el catálogo completo desde `<script id="__NUXT_DATA__">` vía `curl_cffi`.
        """
        target_url = self._resolve_target_url(query)
        cookies = await self._mint_imperva_cookies_cdp(target_url)
        if not cookies or "reese84" not in cookies:
            self._log("⚠️ No se pudo acuñar la cookie `reese84` de Imperva.", level="warning")
            self.blocked = True
            return []

        self.blocked = False
        offers = await self._fast_infiltration(query, cookies=cookies)
        if offers:
            self._log(f"🎉 SmythsToys [Motor REA/CDP]: ¡Éxito! Extraídas {len(offers)} reliquias de __NUXT_DATA__.")
            return offers

        self.blocked = True
        return []

    async def _search_option_1(self, query: str) -> List[ScrapedOffer]:
        """Alias retrocompatible hacia el Motor REA/CDP."""
        return await self._search_rea_cdp(query)

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
                    
                products = self._extract_offers_from_html(resp.text, seen_urls)
                
        except Exception as e:
            self._log(f"❌ Error al consultar ScraperAPI (Opción 2): {e}", level="error")
            self.errors += 1
            
        return products

    @staticmethod
    def _clean_product_title(raw_name: str) -> str:
        name = raw_name.replace("\n", " ").strip()
        name = re.sub(r"\d+[.,]\d{2}\s*(?:€|EUR|\$)", "", name)
        name = re.sub(r"(?i)\d+%\s*off\b", "", name)
        name = re.sub(r"(?i)\d+%\b", "", name)
        name = re.sub(r"(?i)\bvorheriger\s+verkaufspreis\b", "", name)
        name = re.sub(r"(?i)exklusiv", "", name)
        name = re.sub(r"(?i)masters\s+of\s+the\s+universe", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name.strip("-,. ")

    def _extract_offers_from_html(self, html: str, seen_urls: set) -> List[ScrapedOffer]:
        """
        Extrae ofertas priorizando el payload SSR estructurado de Nuxt 3 (`__NUXT_DATA__`)
        y haciendo fallback al parseo de tarjetas DOM (`_parse_html`).
        """
        nuxt_offers = self._parse_nuxt_data(html, seen_urls)
        if nuxt_offers:
            return nuxt_offers
        soup = BeautifulSoup(html, "html.parser")
        return self._parse_html(soup, seen_urls)

    def _parse_nuxt_data(self, html: str, seen_urls: set) -> List[ScrapedOffer]:
        """
        Deserializa el array plano `devalue` dentro de `<script id="__NUXT_DATA__">` de Nuxt 3 SSR.
        Extrae todos los productos estructurados (código, nombre, URL, precio exacto, imagen HD y stock).
        """
        match = re.search(
            r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if not match:
            return []

        try:
            arr = json.loads(match.group(1))
        except Exception as e:
            self._log(f"⚠️ Error parseando JSON de __NUXT_DATA__: {e}", level="debug")
            return []

        if not isinstance(arr, list):
            return []

        def resolve(idx: Any, depth: int = 0) -> Any:
            if depth > 9 or not isinstance(idx, int) or idx < 0 or idx >= len(arr):
                return idx
            val = arr[idx]
            if isinstance(val, list):
                if len(val) == 2 and isinstance(val[0], str) and val[0] in ("ShallowReactive", "Reactive", "Ref"):
                    return resolve(val[1], depth + 1)
                if len(val) == 2 and val[0] == "EmptyRef":
                    return None
                if len(val) >= 1 and val[0] == "Set":
                    return [resolve(x, depth + 1) for x in val[1:]]
                return [resolve(x, depth + 1) for x in val]
            if isinstance(val, dict):
                return {k: resolve(v, depth + 1) for k, v in val.items()}
            return val

        parsed_offers: List[ScrapedOffer] = []
        for idx, item in enumerate(arr):
            if not isinstance(item, dict):
                continue
            if not ("code" in item and "name" in item and "url" in item and "metadata" in item):
                continue

            obj = resolve(idx)
            if not isinstance(obj, dict):
                continue

            raw_name = str(obj.get("name") or "").strip()
            raw_url = str(obj.get("url") or "").strip()
            if not raw_name or not raw_url:
                continue

            # Regla de negocio (.agents/AGENTS.md): filtrar artículos vintage de los 80
            if check_is_vintage(raw_name):
                continue

            full_url = (
                f"https://www.smythstoys.com{raw_url}"
                if raw_url.startswith("/")
                else raw_url
            )
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            clean_name = self._clean_product_title(raw_name) or raw_name

            # Extraer precio exacto desde metadata.priceDetails.value
            price_val = 0.0
            meta = obj.get("metadata")
            if isinstance(meta, dict):
                price_details = meta.get("priceDetails")
                if isinstance(price_details, dict) and price_details.get("value") is not None:
                    try:
                        price_val = float(price_details["value"])
                    except (ValueError, TypeError):
                        price_val = 0.0
            if price_val <= 0 and isinstance(obj.get("price"), dict):
                try:
                    price_val = float(obj["price"].get("value") or 0.0)
                except (ValueError, TypeError):
                    price_val = 0.0
            if price_val <= 0:
                continue

            # Extraer imagen HD
            img_url = None
            prod_img = obj.get("productImage")
            if isinstance(prod_img, dict):
                img_url = prod_img.get("desktop") or prod_img.get("tablet") or prod_img.get("mobile")
            if isinstance(img_url, str) and img_url.startswith("/"):
                img_url = f"https://www.smythstoys.com{img_url}"

            # Disponibilidad
            is_avl = True
            stock_info = obj.get("stock")
            if isinstance(stock_info, dict):
                status_str = str(stock_info.get("stockLevelStatus") or "").lower()
                if status_str in ("outofstock", "nicht lieferbar", "ausverkauft"):
                    is_avl = False
            if obj.get("purchasable") is False or obj.get("inStock") is False:
                is_avl = False

            parsed_offers.append(
                ScrapedOffer(
                    product_name=clean_name,
                    price=price_val,
                    currency="EUR",
                    url=full_url,
                    shop_name="SmythsToys",
                    image_url=img_url if isinstance(img_url, str) else None,
                    is_available=is_avl,
                )
            )
            self.items_scraped += 1

        if parsed_offers:
            self._log(f"✅ __NUXT_DATA__ SSR parseado: {len(parsed_offers)} productos extraídos.")
        return parsed_offers

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

            if check_is_vintage(name):
                continue

            name = self._clean_product_title(name)
            if not name:
                continue
            
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
