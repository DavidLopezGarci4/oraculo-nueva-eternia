from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
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
        from src.infrastructure.database_cloud import init_cloud_db
        init_cloud_db()
        ensure_scrapers_registered()

        # Iniciar escucha de comandos de Telegram en segundo plano (supervisada)
        app.state.telegram_task = asyncio.create_task(_supervised_telegram_listener())
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
    yield
    # Cleanup task on shutdown
    if hasattr(app.state, "telegram_task"):
        app.state.telegram_task.cancel()
        try:
            await app.state.telegram_task
        except asyncio.CancelledError:
            pass

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Oráculo API Broker", version="1.0.0", lifespan=lifespan)

async def _fetch_and_cache_product_image(product_id: int) -> "str | None":
    """
    Fase AAA-4.2 (B.7): rellena la caché local de imágenes bajo demanda.

    Hasta ahora, la conversión a WebP solo pasaba por el importador antiguo
    de Excel (storage_service.py, vía GitHub Actions) o por un script de
    migración puntual (scripts/phase0_migration.py) que nadie vuelve a
    ejecutar — las imágenes descubiertas por los ~17 scrapers de tiendas
    nunca se descargaban ni convertían, solo se servía la URL remota tal
    cual. Esta función descarga la imagen remota del producto, la convierte
    a WebP (mismo patrón que storage_service.py/phase0_migration.py) y la
    guarda en IMAGE_CACHE_DIR, para que la siguiente petición ya la sirva
    desde caché local sin volver a descargarla.
    """
    from src.infrastructure.database_cloud import SessionCloud
    from src.domain.models import ProductModel, OfferModel

    candidate_urls = []
    with SessionCloud() as db:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if product and product.image_url:
            candidate_urls.append(product.image_url)
        
        offers = db.query(OfferModel).filter(OfferModel.product_id == product_id, OfferModel.image_url.is_not(None)).all()
        for o in offers:
            if o.image_url and o.image_url not in candidate_urls:
                candidate_urls.append(o.image_url)

    if not candidate_urls:
        return None

    dest_path = os.path.join(settings.IMAGE_CACHE_DIR, f"{product_id}.webp")
    os.makedirs(settings.IMAGE_CACHE_DIR, exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path

    import io
    import httpx
    from PIL import Image

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
        for image_url in candidate_urls:
            if not image_url or not image_url.startswith("http"):
                continue
            try:
                resp = await client.get(image_url)
                status_code = getattr(resp, "status_code", 200)
                if status_code == 200 and len(resp.content) > 50:
                    with Image.open(io.BytesIO(resp.content)) as img:
                        if img.mode in ("RGBA", "LA"):
                            background = Image.new("RGB", img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode != "RGB":
                            img = img.convert("RGB")
                        img.save(dest_path, "WEBP", quality=85)

                    logger.info(f"📸 Imagen del producto {product_id} descargada y cacheada en WebP desde {image_url}.")
                    return dest_path
            except Exception as e:
                logger.warning(f"⚠️ Error intentando descargar desde {image_url} para producto {product_id}: {e}")

    return None


@app.get("/api/static/images/{product_id}.webp")
async def get_static_image_override(product_id: int, source: str = None, user_id: int = 2):
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    from src.infrastructure.database_cloud import SessionCloud
    from src.domain.models import UserModel

    extensions = [".webp", ".jpg", ".jpeg", ".png"]

    # 1. Try custom path if not explicitly cache-only
    if source != "cache":
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user:
                for custom_dir in [user.pc_image_path, user.mobile_image_path]:
                    if custom_dir:
                        for ext in extensions:
                            file_path = os.path.join(custom_dir, f"{product_id}{ext}")
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                return FileResponse(file_path)

    # 2. Try server cache if not explicitly custom-only
    if source != "custom":
        for ext in extensions:
            server_cache_file = os.path.join(settings.IMAGE_CACHE_DIR, f"{product_id}{ext}")
            if os.path.exists(server_cache_file) and os.path.getsize(server_cache_file) > 0:
                return FileResponse(server_cache_file)

        # 3. Cache miss: descarga + convierte + cachea automáticamente.
        cached_path = await _fetch_and_cache_product_image(product_id)
        if cached_path:
            return FileResponse(cached_path)

    raise HTTPException(status_code=404, detail="Imagen no encontrada")


from src.core.config import get_cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=r"^chrome-extension://.*$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Device-ID", "X-Device-Name"],
)

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
app.include_router(showcase_router.router)


if __name__ == "__main__":
    import uvicorn
    try:
        from scripts.ox3_shield import apply_3ox_shield
        apply_3ox_shield()
    except Exception:
        pass

    uvicorn.run("src.interfaces.api.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
