from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

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
)

app = FastAPI(title="Oráculo API Broker", version="1.0.0")

try:
    from src.infrastructure.database_cloud import init_cloud_db
    init_cloud_db()
    ensure_scrapers_registered()
except Exception as e:
    logger.error(f"Startup initialization failed: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


if __name__ == "__main__":
    import uvicorn
    try:
        from scripts.ox3_shield import apply_3ox_shield
        apply_3ox_shield()
    except Exception:
        pass

    uvicorn.run("src.interfaces.api.main:app", host="0.0.0.0", port=8000, reload=True)
