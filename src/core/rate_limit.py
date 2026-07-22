"""
Rate limiting ligero para endpoints sensibles (Fase AAA-1.7).

Implementación en memoria, de ventana fija, sin dependencias externas.
Suficiente para el despliegue actual (una sola instancia de backend tras
nginx). Si en el futuro se escala a múltiples instancias/réplicas, sustituir
por un backend compartido (Redis) — p. ej. con `slowapi` + `redis`.
"""
import os
from collections import defaultdict
from time import time

from fastapi import HTTPException, Request
from loguru import logger

# {bucket_key: [timestamps]}
_hits: dict[str, list[float]] = defaultdict(list)

# pytest exporta esta variable durante toda la ejecución de la suite. La
# usamos para desactivar el limitador en tests: los tests de integración
# comparten una única IP de cliente y ejercitan los mismos endpoints de auth
# decenas de veces por sesión, lo que dispara falsos 429 sin relación alguna
# con el comportamiento que se está probando.
_TESTING = "PYTEST_CURRENT_TEST" in os.environ


def rate_limit(max_requests: int, window_seconds: int, bucket: str):
    """
    Devuelve una dependencia FastAPI que limita `max_requests` por
    `window_seconds` y por IP de cliente, dentro del `bucket` dado
    (para no compartir contador entre endpoints distintos).
    """

    def _dependency(request: Request):
        if _TESTING:
            return
        client_ip = request.client.host if request.client else "unknown"
        key = f"{bucket}:{client_ip}"
        now = time()
        window_start = now - window_seconds

        hits = [t for t in _hits[key] if t > window_start]
        if len(hits) >= max_requests:
            logger.warning(f"🚫 Rate limit excedido en '{bucket}' para IP {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos. Espera unos minutos antes de volver a intentarlo.",
            )

        hits.append(now)
        _hits[key] = hits

    return _dependency
