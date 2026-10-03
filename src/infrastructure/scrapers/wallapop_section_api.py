"""
Motor de extracción atómico para Wallapop España mediante el endpoint orgánico de búsqueda:
/api/v3/search/section

Validado en producción en PokeCardTrack y adaptado para Oráculo de Nueva Eternia.
Permite extracción de ofertas con coste 0€, sin firmas HMAC complejas ni consumo
de tokens de Apify o ScraperAPI, con TLS fingerprinting nativo de Chrome 124.
"""
from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Any, Dict

from curl_cffi.requests import AsyncSession

from src.infrastructure.scrapers.base import ScrapedOffer

logger = logging.getLogger(__name__)

WALLAPOP_SECTION_URL = "https://api.wallapop.com/api/v3/search/section"

JUNK_KEYWORDS = [
    "camiseta", "t-shirt", "poster", "taza", "mug", 
    "revista", "dvd", "llavero", "keyring", 
    "reproduccion", "repro", "sticker", "pegatina"
]


@dataclass
class SectionSearchResult:
    """Resultado de búsqueda orgánica en Wallapop."""
    offers: List[ScrapedOffer] = field(default_factory=list)
    blocked: bool = False
    next_page: Optional[str] = None


def build_section_params(query: str, next_page: Optional[str] = None) -> Dict[str, Any]:
    """Genera los parámetros para búsqueda inicial o paginación por token."""
    if next_page:
        return {"next_page": next_page}
    return {
        "keywords": query,
        "source": "deep_link",
        "latitude": "40.4153",
        "longitude": "-3.694",
        "order_by": "most_relevance",
        "search_country": "ES",
        "section_type": "organic_search_results",
    }


def build_section_headers() -> Dict[str, str]:
    """Cabeceras requeridas para evadir bloqueos de la web de Wallapop."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://es.wallapop.com/",
        "Origin": "https://es.wallapop.com",
        "x-deviceos": "0",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }


def extract_image_url(item: Dict[str, Any], prefer_medium: bool = True) -> Optional[str]:
    """
    Extracción robusta de imagen.
    Para search/section (PokeCardTrack): prioriza medium -> big -> small.
    Para compatibilidad legacy: permite priorizar big -> medium -> small si prefer_medium=False.
    """
    images = item.get("images", [])
    if images and isinstance(images, list):
        first_img = images[0]
        if isinstance(first_img, dict):
            urls = first_img.get("urls")
            if isinstance(urls, dict):
                if prefer_medium:
                    return urls.get("medium") or urls.get("big") or urls.get("small")
                return urls.get("big") or urls.get("medium") or urls.get("small")
            return first_img.get("original") or first_img.get("medium")
        elif isinstance(first_img, str):
            return first_img

    img_obj = item.get("image")
    if img_obj:
        if isinstance(img_obj, dict):
            urls = img_obj.get("urls")
            if isinstance(urls, dict):
                if prefer_medium:
                    return urls.get("medium") or urls.get("big") or urls.get("small")
                return urls.get("big") or urls.get("medium") or urls.get("small")
            return img_obj.get("original") or img_obj.get("medium")
        elif isinstance(img_obj, str):
            return img_obj

    return None


def parse_section_items(items: List[Dict[str, Any]], shop_name: str = "Wallapop") -> List[ScrapedOffer]:
    """
    Convierte la lista de items JSON de Wallapop section en instancias de ScrapedOffer.
    Aplica filtros de ruido semántico y validación de precios.
    """
    offers: List[ScrapedOffer] = []

    for obj in items:
        title = obj.get("title")
        price = obj.get("price")

        if not title or price is None:
            continue

        title_clean = str(title).strip()
        if not title_clean:
            continue

        # Parse price
        if isinstance(price, dict):
            price_val = float(price.get("amount", 0.0) or 0.0)
        else:
            try:
                price_val = float(price or 0.0)
            except (ValueError, TypeError):
                continue

        if price_val <= 0:
            continue

        # Filtro de ruido
        title_lower = title_clean.lower()
        if any(kw in title_lower for kw in JUNK_KEYWORDS):
            continue

        slug = obj.get("web_slug")
        if not slug:
            continue

        full_url = f"https://es.wallapop.com/item/{slug}"
        image_url = extract_image_url(obj)

        offer = ScrapedOffer(
            product_name=title_clean,
            price=price_val,
            url=full_url,
            shop_name=shop_name,
            image_url=image_url,
            source_type="Peer-to-Peer",
            sale_type="Fixed_P2P",
        )
        offers.append(offer)

    return offers


def _audit_ip_log(status: str, proxy: Optional[str], response_code: Optional[int], details: str) -> None:
    """Registra de forma best-effort el resultado de la incursión en WallapopIpLogModel."""
    try:
        from src.infrastructure.database_cloud import SessionCloud
        from src.domain.models import WallapopIpLogModel

        if proxy:
            masked_proxy = urllib.parse.urlparse(proxy).hostname or "proxy-desconocido"
            ip_label = f"proxy:{masked_proxy}"
            environment = "Proxy Residencial"
        else:
            ip_label = "Directo (Section API)"
            environment = "Local/Direct (chrome124)"

        with SessionCloud() as db:
            db.add(
                WallapopIpLogModel(
                    ip_address=ip_label,
                    status=status,
                    environment=environment,
                    response_code=response_code,
                    details=details,
                )
            )
            db.commit()
    except Exception:
        pass


async def search_wallapop_section(
    session: AsyncSession,
    query: str,
    proxy: Optional[str] = None,
    max_items: int = 40,
    next_page: Optional[str] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    shop_name_override: Optional[str] = None,
) -> SectionSearchResult:
    """
    Ejecuta una petición orgánica contra /api/v3/search/section de Wallapop.
    Soporta paginación con token next_page y suplantación TLS Chrome 124.
    """
    def _log(msg: str, level: str = "info"):
        lvl = getattr(logging, level.upper(), logging.INFO)
        logger.log(lvl, f"[WallapopSectionAPI] {msg}")
        if log_callback:
            try:
                log_callback(msg)
            except Exception:
                pass

    params = build_section_params(query, next_page=next_page)
    headers = build_section_headers()

    kwargs: Dict[str, Any] = {
        "headers": headers,
        "params": params,
        "impersonate": "chrome124",
        "timeout": 15,
    }
    if proxy:
        kwargs["proxy"] = proxy

    try:
        resp = await session.get(WALLAPOP_SECTION_URL, **kwargs)
    except Exception as e:
        _log(f"⚠️ Error de red al consultar '{query}': {e}", level="warning")
        _audit_ip_log("error", proxy, None, f"Error de red: {e}")
        return SectionSearchResult(offers=[], blocked=False)

    if resp.status_code in (403, 429):
        _log(f"🛡️ Bloqueo WAF (HTTP {resp.status_code}) para '{query}' en search/section.", level="warning")
        _audit_ip_log("blocked", proxy, resp.status_code, f"Bloqueo WAF en /api/v3/search/section para '{query}'.")
        return SectionSearchResult(offers=[], blocked=True)

    if resp.status_code != 200:
        _log(f"⚠️ Respuesta no exitosa (HTTP {resp.status_code}) para '{query}'.", level="warning")
        _audit_ip_log("error", proxy, resp.status_code, f"Respuesta no-200 para '{query}'.")
        return SectionSearchResult(offers=[], blocked=False)

    try:
        data = resp.json()
    except Exception:
        _log(f"⚠️ Respuesta no-JSON para '{query}' (posible reto WAF HTML).", level="warning")
        _audit_ip_log("blocked", proxy, resp.status_code, f"Respuesta no-JSON para '{query}'.")
        return SectionSearchResult(offers=[], blocked=True)

    section = data.get("data", {}).get("section", {})
    raw_items = section.get("items", [])
    if max_items:
        raw_items = raw_items[:max_items]

    shop_name = shop_name_override or "Wallapop"
    offers = parse_section_items(raw_items, shop_name=shop_name)
    next_page_token = data.get("meta", {}).get("next_page")

    _log(f"🎉 '{query}': {len(offers)} reliquias extraídas vía Section API orgánica.")
    _audit_ip_log(
        "allowed",
        proxy,
        resp.status_code,
        f"{len(offers)} ofertas extraídas vía Section API para '{query}'.",
    )
    return SectionSearchResult(offers=offers, blocked=False, next_page=next_page_token)
