"""
Rate limiting ligero para endpoints sensibles (Fase AAA-1.7).

Implementación en memoria, de ventana fija, sin dependencias externas.
Suficiente para el despliegue actual (una sola instancia de backend tras
nginx). Si en el futuro se escala a múltiples instancias/réplicas, sustituir
por un backend compartido (Redis) — p. ej. con `slowapi` + `redis`.
"""
import ipaddress
import os
from collections import defaultdict
from time import time

from fastapi import HTTPException, Request
from loguru import logger

# {bucket_key: [timestamps]}
_hits: dict[str, list[float]] = defaultdict(list)
_MAX_BUCKETS = 4096

# pytest exporta PYTEST_CURRENT_TEST durante la ejecución de los tests (puede
# no existir aún durante collection-time). Evaluarlo en runtime permite detectar
# pytest siempre, manteniendo compatibilidad con monkeypatch a False/True.
_TESTING: bool | None = None


def _is_testing() -> bool:
    if _TESTING is not None:
        return bool(_TESTING)
    return "PYTEST_CURRENT_TEST" in os.environ


def _is_trusted_proxy_ip(host: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address((host or "").split("%")[0])
        return ip_obj.is_loopback or ip_obj.is_private
    except ValueError:
        return False


def _extract_client_ip(request: Request) -> str:
    peer_host = request.client.host if request.client else "unknown"
    if _is_trusted_proxy_ip(peer_host):
        real_ip = (request.headers.get("x-real-ip") or "").strip()
        if real_ip:
            return real_ip
        forwarded = (request.headers.get("x-forwarded-for") or "").strip()
        if forwarded:
            return forwarded.split(",")[0].strip()
    return peer_host


def _prune_hits(now: float, window_seconds: int) -> None:
    cutoff = now - window_seconds
    expired_keys = [k for k, ts_list in _hits.items() if not ts_list or max(ts_list) <= cutoff]
    for k in expired_keys:
        _hits.pop(k, None)
    if len(_hits) >= _MAX_BUCKETS:
        oldest_key = min(_hits, key=lambda k: max(_hits[k]) if _hits[k] else 0.0)
        _hits.pop(oldest_key, None)


def enforce_rate_limit_key(
    key: str,
    max_requests: int,
    window_seconds: int,
    bucket: str,
    client_ip: str = "unknown",
    *,
    respect_testing: bool = True,
) -> None:
    """Apply sliding/fixed-window rate limiting to an arbitrary key."""
    if respect_testing and _is_testing():
        return
    now = time()
    window_start = now - window_seconds

    if len(_hits) >= _MAX_BUCKETS and key not in _hits:
        _prune_hits(now, window_seconds)

    hits = [t for t in _hits[key] if t > window_start]
    if len(hits) >= max_requests:
        logger.warning(f"🚫 Rate limit excedido en '{bucket}' para IP {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos. Espera unos minutos antes de volver a intentarlo.",
        )

    hits.append(now)
    _hits[key] = hits


def rate_limit(max_requests: int, window_seconds: int, bucket: str):
    """
    Devuelve una dependencia FastAPI que limita `max_requests` por
    `window_seconds` y por IP de cliente, dentro del `bucket` dado
    (para no compartir contador entre endpoints distintos).
    """

    def _dependency(request: Request):
        if _is_testing():
            return
        client_ip = _extract_client_ip(request)
        enforce_rate_limit_key(
            f"{bucket}:{client_ip}",
            max_requests,
            window_seconds,
            bucket,
            client_ip,
            respect_testing=True,
        )

    return _dependency
