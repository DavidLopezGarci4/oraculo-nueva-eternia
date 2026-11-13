from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.config import settings

if settings.JWT_SECRET == "oraculo-jwt-secret-CHANGE-IN-PRODUCTION":
    logger.critical("JWT_SECRET uses the insecure default value. Set JWT_SECRET in .env before deploying to production!")

from src.interfaces.api.deps import ensure_scrapers_registered
from src.interfaces.api.routers import (
    admin as admin_router,
    auth as auth_router,
    collection as collection_router,
    dashboard as dashboard_router,
    health as health_router,
    logistics as logistics_router,
    products as products_router,
    purgatory as purgatory_router,
    scrapers as scrapers_router,
    system as system_router,
    users as users_router,
    vault as vault_router,
    wallapop_jobs as wallapop_jobs_router,
)

import asyncio
from contextlib import asynccontextmanager

# Fase AAA-2.5: antes, el listener de Telegram se lanzaba con un
# asyncio.create_task() sin supervisión — si moría por una excepción que
# escapara a su propio bucle interno, quedaba muerto en silencio hasta el
# siguiente reinicio del servidor, sin ningún rastro en logs. Este wrapper lo
# reinicia con backoff ante fallos inesperados, y se rinde (dejando un
# CRITICAL bien visible) tras varios intentos consecutivos fallidos en vez de
# reintentar para siempre.
_TELEGRAM_MAX_CONSECUTIVE_FAILURES = 5
_TELEGRAM_RESTART_BACKOFF_SECONDS = 15


async def _supervised_telegram_listener():
    from src.infrastructure.services.telegram_listener import telegram_listener

    consecutive_failures = 0
    while True:
        try:
            await telegram_listener.start_polling()
            # Retorno limpio (stop_polling() llamado deliberadamente): no reiniciar.
            return
        except asyncio.CancelledError:
            raise
        except Exception as e:
            consecutive_failures += 1
            logger.error(
                f"📡 Telegram Listener murió inesperadamente (fallo {consecutive_failures}/"
                f"{_TELEGRAM_MAX_CONSECUTIVE_FAILURES}): {e}"
            )
            if consecutive_failures >= _TELEGRAM_MAX_CONSECUTIVE_FAILURES:
                logger.critical(
                    "📡 Telegram Listener: demasiados fallos consecutivos. "
                    "Dejando de reintentar hasta el próximo reinicio del servidor."
                )
                return
            await asyncio.sleep(_TELEGRAM_RESTART_BACKOFF_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from src.infrastructure.database_cloud import init_cloud_db, SessionCloud
        init_cloud_db()
        ensure_scrapers_registered()

        # Iniciar escucha de comandos de Telegram en segundo plano (supervisada)
        app.state.telegram_task = asyncio.create_task(_supervised_telegram_listener())

        # Iniciar Centinela Autónomo de Vinted (Phase 84)
        if getattr(settings, "VINTED_SENTINEL_ENABLED", True):
            from src.application.services.vinted_sentinel_service import vinted_sentinel
            vinted_sentinel.start()

        # Auto-sembrado incremental idempotente de Lore Canónico (Fase 88/90):
        # SessionCloud es la fuente primaria; la replica a SQLite local es unidireccional y best-effort.
        try:
            from src.application.services.lore_harvester_service import LoreHarvesterService
            try:
                with SessionCloud() as db_session:
                    LoreHarvesterService.seed_incremental_dual(db_session)
            except Exception as e_cloud:
                logger.warning(f"Auto-sembrado de Lore en SessionCloud falló, usando SQLite local: {e_cloud}")
                from src.infrastructure.database import SessionLocal
                with SessionLocal() as db_session:
                    LoreHarvesterService.seed_incremental_dual(db_session)
        except Exception as e_lore:
            logger.warning(f"Aviso en auto-sembrado de Lore: {e_lore}")
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
    yield
    # Cleanup task on shutdown
    if getattr(settings, "VINTED_SENTINEL_ENABLED", True):
        from src.application.services.vinted_sentinel_service import vinted_sentinel
        vinted_sentinel.stop()

    if hasattr(app.state, "telegram_task"):
        app.state.telegram_task.cancel()
        try:
            await app.state.telegram_task
        except asyncio.CancelledError:
            pass

from fastapi.staticfiles import StaticFiles
import os
import time
import anyio
from src.infrastructure.database_cloud import SessionCloud as _DefaultSessionCloud

SessionCloud = _DefaultSessionCloud


def _resolve_session_cloud():
    if SessionCloud is not _DefaultSessionCloud:
        return SessionCloud
    from src.infrastructure.database_cloud import SessionCloud as _LiveSessionCloud
    return _LiveSessionCloud


app = FastAPI(title="Oráculo API Broker", version=settings.VERSION, lifespan=lifespan)

STATIC_IMAGE_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=604800, stale-while-revalidate=86400"
}
_USER_IMAGE_PATHS_TTL = 300.0
_user_image_paths_cache: dict[int, tuple[float, list[str]]] = {}


def invalidate_user_image_paths_cache(user_id: int | None = None) -> None:
    if user_id is None:
        _user_image_paths_cache.clear()
    else:
        _user_image_paths_cache.pop(user_id, None)


def _get_cached_user_image_paths(user_id: int) -> list[str]:
    now = time.monotonic()
    cached = _user_image_paths_cache.get(user_id)
    if cached and cached[0] > now:
        return cached[1]

    from src.domain.models import UserModel
    from src.interfaces.api.deps import is_admin

    paths: list[str] = []
    session_factory = _resolve_session_cloud()
    with session_factory() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user and is_admin(user):
            paths = [p for p in (user.pc_image_path, user.mobile_image_path) if p]
    _user_image_paths_cache[user_id] = (now + _USER_IMAGE_PATHS_TTL, paths)
    return paths


def _load_product_candidate_image_urls(product_id: int) -> list[str]:
    from src.domain.models import ProductModel, OfferModel

    candidate_urls: list[str] = []
    session_factory = _resolve_session_cloud()
    with session_factory() as db:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if product and product.image_url:
            candidate_urls.append(product.image_url)

        offers = (
            db.query(OfferModel.image_url)
            .filter(OfferModel.product_id == product_id, OfferModel.image_url.is_not(None))
            .all()
        )
        for (img_url,) in offers:
            if img_url and img_url not in candidate_urls:
                candidate_urls.append(img_url)
    return candidate_urls


def _encode_webp_to_disk(raw_bytes: bytes, dest_path: str) -> None:
    import io
    from PIL import Image
    from src.core.safe_http import configure_pillow_limits

    configure_pillow_limits()
    with Image.open(io.BytesIO(raw_bytes)) as img:
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(dest_path, "WEBP", quality=85)


async def _fetch_and_cache_product_image(product_id: int) -> "str | None":
    """
    Fase AAA-4.2 (B.7): rellena la caché local de imágenes bajo demanda.
    Protegida contra SSRF mediante validate_public_url y límite de tamaño.
    """
    candidate_urls = await anyio.to_thread.run_sync(_load_product_candidate_image_urls, product_id)
    if not candidate_urls:
        return None

    dest_path = os.path.join(settings.IMAGE_CACHE_DIR, f"{product_id}.webp")
    os.makedirs(settings.IMAGE_CACHE_DIR, exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path

    from src.core.safe_http import fetch_safe_bytes

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }

    for image_url in candidate_urls:
        if not image_url or not image_url.startswith("http"):
            continue
        try:
            content, status_code, _ = await fetch_safe_bytes(
                image_url,
                max_bytes=10 * 1024 * 1024,
                timeout=15.0,
                headers=headers,
            )
            if status_code == 200 and len(content) > 50:
                await anyio.to_thread.run_sync(_encode_webp_to_disk, content, dest_path)
                logger.info(f"📸 Imagen del producto {product_id} descargada y cacheada en WebP desde {image_url}.")
                return dest_path
        except Exception as e:
            logger.warning(f"⚠️ Error intentando descargar desde {image_url} para producto {product_id}: {e}")

    return None


def _has_valid_image_magic(file_path) -> bool:
    try:
        with file_path.open("rb") as fh:
            header = fh.read(12)
    except OSError:
        return False
    return (
        (len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP")
        or header.startswith(b"\x89PNG\r\n\x1a\n")
        or header.startswith(b"\xff\xd8\xff")
    )


@app.get("/api/static/images/{product_id}.webp")
async def get_static_image_override(product_id: int, source: str = None, user_id: int = 2):
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    from pathlib import Path

    extensions = [".webp", ".jpg", ".jpeg", ".png"]
    cache_root = Path(settings.IMAGE_CACHE_DIR).resolve()

    if source != "cache":
        custom_dirs = await anyio.to_thread.run_sync(_get_cached_user_image_paths, user_id)
        for custom_dir in custom_dirs:
            raw_base = Path(custom_dir)
            if raw_base.is_symlink() or not raw_base.exists() or not raw_base.is_dir():
                continue
            base = raw_base.resolve()
            for ext in extensions:
                candidate = base / f"{product_id}{ext}"
                if candidate.is_symlink():
                    continue
                resolved = candidate.resolve()
                if (
                    resolved.is_relative_to(base)
                    and resolved.exists()
                    and resolved.is_file()
                    and resolved.stat().st_size > 0
                    and _has_valid_image_magic(resolved)
                ):
                    return FileResponse(str(resolved), headers=STATIC_IMAGE_CACHE_HEADERS)

    if source != "custom":
        for ext in extensions:
            server_cache_file = (cache_root / f"{product_id}{ext}").resolve()
            if server_cache_file.is_relative_to(cache_root) and server_cache_file.exists() and server_cache_file.is_file() and server_cache_file.stat().st_size > 0:
                return FileResponse(str(server_cache_file), headers=STATIC_IMAGE_CACHE_HEADERS)

        cached_path = await _fetch_and_cache_product_image(product_id)
        if cached_path:
            return FileResponse(cached_path, headers=STATIC_IMAGE_CACHE_HEADERS)

    raise HTTPException(status_code=404, detail="Imagen no encontrada")


import re as _re
from src.core.config import get_cors_origins

_ext_ids = [
    _re.escape(ext_id.strip())
    for ext_id in (settings.ALLOWED_CHROME_EXTENSION_IDS or "").split(",")
    if ext_id.strip()
]
_is_dev_env = (settings.ENV or "").strip().lower() in ("development", "dev", "local", "test")
_cors_extension_regex = (
    rf"^chrome-extension://(?:{'|'.join(_ext_ids)})$"
    if _ext_ids
    else (r"^chrome-extension://[a-p]{32}$" if _is_dev_env else None)
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=_cors_extension_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-API-Key",
        "X-Device-ID",
        "X-Device-Name",
        "X-Extension-Key",
    ],
)


@app.middleware("http")
async def add_security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response

# ─── Global exception handlers ────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"status": "error", "type": "validation_error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "type": "server_error", "detail": "Internal server error"},
    )


# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(scrapers_router.router)
app.include_router(admin_router.router)
app.include_router(products_router.router)
app.include_router(collection_router.router)
app.include_router(purgatory_router.router)
app.include_router(dashboard_router.router)
app.include_router(users_router.router)
app.include_router(system_router.router)
app.include_router(vault_router.router)
app.include_router(logistics_router.router)
app.include_router(wallapop_jobs_router.router)

from src.interfaces.api.routers import showcase as showcase_router
from src.interfaces.api.routers import analytics as analytics_router
from src.interfaces.api.routers import cards as cards_router
from src.interfaces.api.routers import lore as lore_router
app.include_router(showcase_router.router)
app.include_router(analytics_router.router)
app.include_router(cards_router.router)
app.include_router(lore_router.router)


if __name__ == "__main__":
    import uvicorn
    try:
        from scripts.ox3_shield import apply_3ox_shield
        apply_3ox_shield()
    except Exception:
        pass

    uvicorn.run("src.interfaces.api.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
