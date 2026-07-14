"""
Núcleo compartido: búsqueda en la API v3 de Wallapop mediante X-Signature (HMAC).

Extraído de WallapopManualScraper para que TANTO el spider manual ("WallapopManual")
COMO el cascade automático ("Wallapop" -> WallapopScraper.search_via_api) puedan
usar la misma firma real cuando las cuotas gratuitas de Apify se agotan.

Endpoint VALIDADO en real: /api/v3/search (no /api/v3/general/search).
Sin proxy residencial, desde una IP de datacenter, seguirá bloqueado (403) — eso es
esperado: la firma resuelve "Apify agotado pero la IP es válida", no el veto de IP.
"""
from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from curl_cffi.requests import AsyncSession

from src.infrastructure.scrapers.base import ScrapedOffer
from src.infrastructure.scrapers.wallapop_signer import WallapopSigner

logger = logging.getLogger(__name__)


@dataclass
class SignedSearchResult:
    """Resultado de una búsqueda firmada, distinguiendo 'vacío' de 'bloqueado por WAF'."""
    offers: List[ScrapedOffer] = field(default_factory=list)
    blocked: bool = False

# Endpoint de búsqueda de la API v3 (host firmado, no la web)
WALLAPOP_API_HOST = "https://api.wallapop.com"
WALLAPOP_SEARCH_PATH = "/api/v3/search"


def _audit_ip_log(status: str, proxy: Optional[str], response_code: Optional[int], details: str) -> None:
    """
    Fase 4 (observabilidad): registra el resultado de cada intento en
    WallapopIpLogModel, reutilizando el mismo modelo que ya audita el resto de
    canales de Wallapop. Best-effort: nunca lanza excepción ni añade latencia
    perceptible (no hace sondeo de IP pública, para no penalizar el camino feliz).
    """
    try:
        from src.infrastructure.database_cloud import SessionCloud
        from src.domain.models import WallapopIpLogModel

        if proxy:
            masked_proxy = urllib.parse.urlparse(proxy).hostname or "proxy-desconocido"
            ip_label = f"proxy:{masked_proxy}"
            environment = "Proxy Residencial (WALLAPOP_RESIDENTIAL_PROXY)"
        else:
            ip_label = "N/A (API firmada, sin proxy)"
            environment = "Datacenter/Local (sin proxy)"

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
        # La auditoría nunca debe romper el flujo de extracción.
        pass


def _build_signed_headers(path_with_query: str) -> dict:
    """Cabeceras de un cliente web real de Wallapop, con X-Signature válida."""
    signature, timestamp = WallapopSigner.generate_signature("GET", path_with_query)
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://es.wallapop.com",
        "Referer": "https://es.wallapop.com/",
        "X-Signature": signature,
        "X-DeviceOS": "0",
        "DeviceOS": "0",
        "Timestamp": str(timestamp),
        "X-AppVersion": "86040",
    }


async def search_wallapop_v3_signed(
    session: AsyncSession,
    query: str,
    proxy: Optional[str] = None,
    max_items: int = 40,
    log_callback: Optional[Callable[[str], None]] = None,
    shop_name_override: Optional[str] = None,
) -> SignedSearchResult:
    """
    Realiza una búsqueda firmada (X-Signature) contra la API v3 de Wallapop.

    Nunca lanza excepción: en cualquier fallo devuelve un SignedSearchResult con
    offers=[] para que el llamador pueda continuar con su propio cascade de
    fallback sin romper el flujo. `blocked=True` distingue "WAF/HTML nos bloqueó"
    de "búsqueda válida sin resultados", para que el cascade automático sepa si
    merece la pena seguir insistiendo con este canal.
    """
    def _log(msg: str, level: str = "info"):
        lvl = getattr(logging, level.upper(), logging.INFO)
        logger.log(lvl, f"[WallapopSignedAPI] {msg}")
        if log_callback:
            try:
                log_callback(msg)
            except Exception:
                pass

    params = {
        "keywords": query,
        "order_by": "newest",
        "source": "search_box",
        "latitude": 40.416775,
        "longitude": -3.703790,
    }
    path_with_query = f"{WALLAPOP_SEARCH_PATH}?{urllib.parse.urlencode(params)}"
    target_url = f"{WALLAPOP_API_HOST}{path_with_query}"
    headers = _build_signed_headers(path_with_query)

    kwargs = dict(headers=headers, impersonate="chrome120", timeout=20)
    if proxy:
        kwargs["proxy"] = proxy

    try:
        resp = await session.get(target_url, **kwargs)
    except Exception as e:
        _log(f"⚠️ Error de red al consultar '{query}': {e}", level="warning")
        _audit_ip_log("error", proxy, None, f"Error de red: {e}")
        return SignedSearchResult(offers=[], blocked=False)

    if resp.status_code in (403, 429):
        nexus_tip = "Proxy residencial agotado/invalidado." if proxy else (
            "IP de datacenter vetada: configura WALLAPOP_RESIDENTIAL_PROXY o "
            "usa el Nexus Local Bridge (scripts/nexus_local_worker.py) para resolverlo desde una IP residencial."
        )
        _log(f"🛡️ Bloqueo WAF (HTTP {resp.status_code}) para '{query}' vía API firmada. {nexus_tip}", level="warning")
        _audit_ip_log("blocked", proxy, resp.status_code, f"Bloqueo WAF en /api/v3/search para '{query}'. {nexus_tip}")
        return SignedSearchResult(offers=[], blocked=True)

    if resp.status_code != 200:
        _log(f"⚠️ Respuesta no exitosa (HTTP {resp.status_code}) para '{query}' vía API firmada.", level="warning")
        _audit_ip_log("error", proxy, resp.status_code, f"Respuesta no-200 para '{query}'.")
        return SignedSearchResult(offers=[], blocked=False)

    try:
        data = resp.json()
    except Exception:
        _log(f"⚠️ Respuesta no-JSON para '{query}' vía API firmada (posible reto WAF HTML).", level="warning")
        _audit_ip_log("blocked", proxy, resp.status_code, f"Respuesta no-JSON (reto WAF HTML) para '{query}'.")
        return SignedSearchResult(offers=[], blocked=True)

    # La v3 devuelve las tarjetas en distintas rutas según versión: normalizamos.
    items = (
        data.get("search_objects")
        or data.get("data", {}).get("section", {}).get("payload", {}).get("items")
        or data.get("items")
        or []
    )
    if max_items:
        items = items[:max_items]

    # Import perezoso para reutilizar el parser JSON robusto sin crear un ciclo de
    # imports a nivel de módulo con wallapop_scraper.py.
    from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper

    offers = WallapopScraper()._parse_wallapop_json_objects(items)
    if shop_name_override:
        for o in offers:
            o.shop_name = shop_name_override
    _log(f"🎉 '{query}': {len(offers)} reliquias extraídas vía API firmada.")
    _audit_ip_log(
        "proxy_bypass" if proxy else "allowed",
        proxy,
        resp.status_code,
        f"{len(offers)} ofertas extraídas vía API firmada para '{query}'.",
    )
    return SignedSearchResult(offers=offers, blocked=False)
