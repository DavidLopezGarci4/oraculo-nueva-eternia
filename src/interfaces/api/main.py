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
                
    raise HTTPException(status_code=404, detail="Imagen no encontrada")

# Mount local image cache directory
image_cache_dir = settings.IMAGE_CACHE_DIR
os.makedirs(image_cache_dir, exist_ok=True)
app.mount("/api/static/images", StaticFiles(directory=image_cache_dir), name="static_images")

from src.core.config import get_cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
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
