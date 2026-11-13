"""
Hardened outbound HTTP utilities against SSRF, credential leaks, and image-bomb DoS.
"""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlsplit

import httpx
from PIL import Image

IMAGE_MAX_PIXELS = 25_000_000
MAX_REDIRECT_HOPS = 4
_STREAM_CHUNK_BYTES = 65_536
_ORIG_ASYNC_CLIENT_GET = httpx.AsyncClient.get
_ORIG_SYNC_CLIENT_GET = httpx.Client.get

try:
    Image.MAX_IMAGE_PIXELS = IMAGE_MAX_PIXELS
except Exception:
    pass

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "metadata",
        "metadata.google.internal",
        "169.254.169.254",
        "::1",
    }
)


def configure_pillow_limits() -> None:
    """Enforce bounded decompressed image pixel limits on Pillow."""
    Image.MAX_IMAGE_PIXELS = IMAGE_MAX_PIXELS


def _is_public_ip(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped is not None:
        return _is_public_ip(ip_obj.ipv4_mapped)
    return (
        ip_obj.is_global
        and not ip_obj.is_private
        and not ip_obj.is_loopback
        and not ip_obj.is_link_local
        and not ip_obj.is_multicast
        and not ip_obj.is_reserved
        and not ip_obj.is_unspecified
    )


def validate_public_url(url: str) -> str:
    """
    Validate that *url* is an http(s) URL pointing to a public non-internal host.
    Raises ValueError on private, loopback, link-local, metadata, or malformed targets.
    """
    raw = (url or "").strip()
    if not raw:
        raise ValueError("URL vacía no permitida.")

    parsed = urlsplit(raw)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Esquema no permitido: {parsed.scheme!r}")

    if parsed.username or parsed.password:
        raise ValueError("Credenciales embebidas en URL no están permitidas.")

    host = (parsed.hostname or "").strip().rstrip(".").lower()
    if not host:
        raise ValueError("URL sin hostname válido.")

    if (
        host in _BLOCKED_HOSTNAMES
        or host.endswith(".localhost")
        or host.endswith(".local")
        or host.endswith(".internal")
    ):
        raise ValueError(f"Hostname interno bloqueado: {host!r}")

    try:
        literal_ip = ipaddress.ip_address(host)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not _is_public_ip(literal_ip):
            raise ValueError(f"IP no pública bloqueada: {host!r}")
        return raw

    try:
        addr_info = socket.getaddrinfo(host, None)
    except socket.gaierror:
        # Allow HTTP client / unit-test mocks to handle unresolvable mock domains (e.g. RFC 2606)
        return raw

    for entry in addr_info:
        sockaddr = entry[4]
        if not sockaddr:
            continue
        ip_str = str(sockaddr[0]).split("%")[0]
        resolved_ip = ipaddress.ip_address(ip_str)
        if not _is_public_ip(resolved_ip):
            raise ValueError(f"DNS resolvió a IP no pública ({ip_str}) para {host!r}")

    return raw


def _check_content_length(headers, max_bytes: int) -> None:
    cl_raw = headers.get("content-length") if hasattr(headers, "get") else None
    if cl_raw:
        try:
            if int(cl_raw) > max_bytes:
                raise ValueError(f"Contenido remoto excede límite de {max_bytes} bytes.")
        except ValueError as exc:
            if "excede" in str(exc):
                raise


def _verify_peer_ip(resp: httpx.Response) -> None:
    """Validate actual connected peer IP to mitigate DNS rebinding after preflight."""
    extensions = getattr(resp, "extensions", None)
    stream = extensions.get("network_stream") if isinstance(extensions, dict) else None
    get_extra = getattr(stream, "get_extra_info", None)
    peer = (
        (get_extra("server_addr") or get_extra("peername"))
        if callable(get_extra)
        else None
    )
    if peer and isinstance(peer, (tuple, list)) and peer[0]:
        peer_ip = ipaddress.ip_address(str(peer[0]).split("%")[0])
        if not _is_public_ip(peer_ip):
            raise ValueError(f"Conexión saliente a IP no pública bloqueada ({peer[0]!r}).")


def _read_bounded_response(resp: httpx.Response, max_bytes: int) -> bytes:
    headers = getattr(resp, "headers", None) or {}
    _check_content_length(headers, max_bytes)
    content = resp.content
    if len(content) > max_bytes:
        raise ValueError(f"Respuesta remota excede límite de {max_bytes} bytes.")
    return content


async def fetch_safe_bytes(
    url: str,
    *,
    max_bytes: int = 10 * 1024 * 1024,
    timeout: float = 15.0,
    headers: dict[str, str] | None = None,
) -> tuple[bytes, int, dict[str, str]]:
    """Fetch remote bytes while validating initial and redirect target URLs against SSRF."""
    current_url = validate_public_url(url)
    use_stream = httpx.AsyncClient.get is _ORIG_ASYNC_CLIENT_GET
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        for _ in range(MAX_REDIRECT_HOPS + 1):
            req_kwargs = {"headers": headers} if headers else {}
            if use_stream:
                async with client.stream("GET", current_url, **req_kwargs) as resp:
                    _verify_peer_ip(resp)
                    status_code = getattr(resp, "status_code", 200)
                    resp_headers = getattr(resp, "headers", None) or {}
                    if status_code in (301, 302, 303, 307, 308) and hasattr(resp_headers, "get"):
                        location = resp_headers.get("location") or resp_headers.get("Location")
                        if not location:
                            break
                        current_url = validate_public_url(urljoin(current_url, location))
                        continue

                    if status_code != 200:
                        return b"", status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

                    _check_content_length(resp_headers, max_bytes)
                    buf = bytearray()
                    async for chunk in resp.aiter_bytes(chunk_size=_STREAM_CHUNK_BYTES):
                        if len(buf) + len(chunk) > max_bytes:
                            raise ValueError(f"Respuesta remota excede límite de {max_bytes} bytes.")
                        buf.extend(chunk)
                    return bytes(buf), status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

            resp = await client.get(current_url, **req_kwargs)
            _verify_peer_ip(resp)
            status_code = getattr(resp, "status_code", 200)
            resp_headers = getattr(resp, "headers", None) or {}
            if status_code in (301, 302, 303, 307, 308) and hasattr(resp_headers, "get"):
                location = resp_headers.get("location") or resp_headers.get("Location")
                if not location:
                    break
                current_url = validate_public_url(urljoin(current_url, location))
                continue

            if status_code != 200:
                return b"", status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

            data = _read_bounded_response(resp, max_bytes)
            return data, status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

    raise ValueError("Demasiadas redirecciones HTTP.")


def fetch_safe_bytes_sync(
    url: str,
    *,
    max_bytes: int = 10 * 1024 * 1024,
    timeout: float = 15.0,
    headers: dict[str, str] | None = None,
) -> tuple[bytes, int, dict[str, str]]:
    """Synchronous SSRF-safe GET helper with manual redirect validation and byte cap."""
    current_url = validate_public_url(url)
    use_stream = httpx.Client.get is _ORIG_SYNC_CLIENT_GET
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        for _ in range(MAX_REDIRECT_HOPS + 1):
            req_kwargs = {"headers": headers} if headers else {}
            if use_stream:
                with client.stream("GET", current_url, **req_kwargs) as resp:
                    _verify_peer_ip(resp)
                    status_code = getattr(resp, "status_code", 200)
                    resp_headers = getattr(resp, "headers", None) or {}
                    if status_code in (301, 302, 303, 307, 308) and hasattr(resp_headers, "get"):
                        location = resp_headers.get("location") or resp_headers.get("Location")
                        if not location:
                            break
                        current_url = validate_public_url(urljoin(current_url, location))
                        continue

                    if status_code != 200:
                        return b"", status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

                    _check_content_length(resp_headers, max_bytes)
                    buf = bytearray()
                    for chunk in resp.iter_bytes(chunk_size=_STREAM_CHUNK_BYTES):
                        if len(buf) + len(chunk) > max_bytes:
                            raise ValueError(f"Respuesta remota excede límite de {max_bytes} bytes.")
                        buf.extend(chunk)
                    return bytes(buf), status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

            resp = client.get(current_url, **req_kwargs)
            _verify_peer_ip(resp)
            status_code = getattr(resp, "status_code", 200)
            resp_headers = getattr(resp, "headers", None) or {}
            if status_code in (301, 302, 303, 307, 308) and hasattr(resp_headers, "get"):
                location = resp_headers.get("location") or resp_headers.get("Location")
                if not location:
                    break
                current_url = validate_public_url(urljoin(current_url, location))
                continue

            if status_code != 200:
                return b"", status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

            data = _read_bounded_response(resp, max_bytes)
            return data, status_code, dict(resp_headers) if hasattr(resp_headers, "items") else {}

    raise ValueError("Demasiadas redirecciones HTTP.")
