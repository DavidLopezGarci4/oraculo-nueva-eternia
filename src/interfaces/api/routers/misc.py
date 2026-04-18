import json
import os
import sys
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from src.application.services.logistics_service import LogisticsService
from src.domain.models import PendingMatchModel, UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key, verify_device
from src.interfaces.api.schemas import CartRequest, WallapopImportRequest

router = APIRouter(tags=["misc"])


@router.get("/api/radar/p2p-opportunities")
async def get_p2p_opportunities(user_id: int = 2):
    from src.domain.models import OfferModel, ProductModel

    with SessionCloud() as db:
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        opportunities = (
            db.query(OfferModel)
            .join(ProductModel)
            .filter(
                OfferModel.is_available == True,
                OfferModel.source_type == "Peer-to-Peer",
                ProductModel.p25_price > 0,
                OfferModel.price <= ProductModel.p25_price,
            )
            .all()
        )

        results = []
        for o in opportunities:
            saving = o.product.p25_price - o.price
            saving_pct = (saving / o.product.p25_price * 100) if o.product.p25_price > 0 else 0.0

            results.append({
                "id": o.id,
                "product_name": o.product.name,
                "ean": o.product.ean,
                "image_url": o.product.image_url,
                "price": o.price,
                "p25_price": o.product.p25_price,
                "avg_market_price": o.product.avg_market_price,
                "saving": round(saving, 2),
                "saving_pct": round(saving_pct, 1),
                "shop_name": o.shop_name,
                "url": o.url,
                "opportunity_score": o.opportunity_score,
                "landing_price": LogisticsService.get_landing_price(o.price, o.shop_name, user_location),
            })

        return sorted(results, key=lambda x: x["saving_pct"], reverse=True)


@router.post("/api/wallapop/import")
async def import_wallapop_products(request: WallapopImportRequest):
    imported = 0

    with SessionCloud() as db:
        for product in request.products:
            existing = db.query(PendingMatchModel).filter(PendingMatchModel.url == product.url).first()
            if existing:
                continue

            pending = PendingMatchModel(
                scraped_name=f"[Wallapop] {product.title}",
                price=product.price,
                currency="EUR",
                url=product.url,
                shop_name="Wallapop",
                source_type="Peer-to-Peer",
                image_url=product.imageUrl,
                found_at=datetime.utcnow(),
            )
            db.add(pending)
            imported += 1

        db.commit()

    logger.info(f"[Wallapop Extension] Importados {imported} productos al Purgatorio")
    return {"status": "success", "imported": imported, "total_received": len(request.products)}


@router.get("/api/users/{user_id}", dependencies=[Depends(verify_device)])
async def get_user_settings(user_id: int):
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "location": user.location,
            "role": user.role,
        }


@router.get("/api/system/audit", dependencies=[Depends(verify_api_key)])
async def system_audit():
    from src.core.config import settings
    from src.domain.models import (
        AuthorizedDeviceModel,
        CollectionItemModel,
        OfferModel,
        ProductModel,
        UserModel,
    )
    from src.infrastructure.database_cloud import cloud_url, engine_cloud
    import sqlalchemy

    db_type = "Postgres/Supabase" if "postgresql" in cloud_url else "SQLite/Local"

    with SessionCloud() as db:
        try:
            db.execute(sqlalchemy.text("SELECT 1"))

            u_count = db.query(UserModel).count()
            p_count = db.query(ProductModel).count()
            c_count = db.query(CollectionItemModel).count()
            o_count = db.query(OfferModel).count()
            ad_count = db.query(AuthorizedDeviceModel).count()

            david = db.query(UserModel).filter(UserModel.id == 2).first()
            david_items = 0
            if david:
                david_items = db.query(CollectionItemModel).filter(
                    CollectionItemModel.owner_id == 2,
                    CollectionItemModel.acquired == True,
                ).count()

            conn_info = str(engine_cloud.url).split("@")[-1] if "@" in str(engine_cloud.url) else "local_sqlite"

            security_cols = []
            try:
                col_check = db.execute(sqlalchemy.text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name IN ('reset_token', 'reset_token_expiry')
                """)).fetchall()
                security_cols = [c[0] for c in col_check]
            except Exception:
                pass

            return {
                "status": "ONLINE",
                "database_engine": db_type,
                "connection_target": conn_info,
                "counts": {
                    "users": u_count,
                    "products": p_count,
                    "collection_items": c_count,
                    "offers": o_count,
                    "authorized_devices": ad_count,
                },
                "schema_audit": {
                    "reset_token_found": "reset_token" in security_cols,
                    "reset_token_expiry_found": "reset_token_expiry" in security_cols,
                },
                "david_diagnostic": {
                    "exists": david is not None,
                    "id": david.id if david else None,
                    "username": david.username if david else None,
                    "role": david.role if david else None,
                    "acquired_items_reality": david_items,
                    "target_expected": 120,
                },
                "environment": {
                    "SUPABASE_DATABASE_URL_SET": settings.SUPABASE_DATABASE_URL is not None
                    and len(settings.SUPABASE_DATABASE_URL) > 10,
                    "DATABASE_URL": settings.DATABASE_URL,
                    "PYTHON_VERSION": sys.version,
                    "SMTP_CONFIG": {
                        "HOST": settings.SMTP_HOST,
                        "PORT": settings.SMTP_PORT,
                        "USER_LOADED": settings.SMTP_USER is not None,
                        "PASS_LOADED": settings.SMTP_PASS is not None and len(settings.SMTP_PASS) > 5,
                        "SENDER": settings.SMTP_FROM,
                    },
                },
            }
        except Exception as e:
            logger.error(f"AUDIT FAILURE: {e}")
            return {
                "status": "ERROR",
                "database_engine": db_type,
                "error_detail": str(e),
                "hint": "Check if DB credentials are correct or if the DB server is reachable.",
            }


@router.post("/api/users/{user_id}/location")
async def update_user_location(user_id: int, location: str):
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user.location = location.upper()
        db.commit()
        return {"status": "success", "location": user.location}


@router.get("/api/vault/generate")
async def api_generate_vault(user_id: int = 2):
    from src.application.services.vault_service import VaultService

    vault_service = VaultService()
    with SessionCloud() as db:
        try:
            vault_path = vault_service.generate_user_vault(user_id, db)
            return FileResponse(
                path=vault_path,
                filename=os.path.basename(vault_path),
                media_type="application/x-sqlite3",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/vault/stage")
async def api_stage_vault(user_id: int = 2, file_path: str = None):
    from src.application.services.vault_service import VaultService
    from src.domain.models import StagedImportModel

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Archivo no encontrado.")

    vault_service = VaultService()
    try:
        vault_service.stage_vault_import(user_id, file_path)

        with SessionCloud() as db:
            stage = StagedImportModel(
                user_id=user_id,
                import_type="VAULT",
                status="PENDING",
                data_payload=json.dumps({"source_file": file_path}),
                impact_summary="Importación de Bóveda SQLite detectada. Pendiente de auditoría del Arquitecto.",
            )
            db.add(stage)
            db.commit()

        return {"status": "success", "message": "Bóveda en Cuarentena. Un administrador debe validar la inyección."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Shield Protocol Bloqueó Infección: {str(e)}")


@router.post("/api/excel/sync")
async def api_sync_excel(user_id: int = 2):
    from src.application.services.excel_manager import ExcelManager

    project_root = Path(__file__).resolve().parents[4]
    DAVID_EXCEL = str(project_root / "data" / "MOTU" / "lista_MOTU.xlsx")

    manager = ExcelManager(DAVID_EXCEL)
    success = manager.sync_acquisitions_from_db(user_id)

    if success:
        return {"status": "success", "message": "Excel Bridge sincronizado con éxito."}
    else:
        raise HTTPException(
            status_code=500,
            detail="Fallo en la sincronización del Excel. Verifique la ruta y el formato.",
        )


@router.post("/api/logistics/calculate-cart")
async def api_calculate_cart(request: CartRequest):
    try:
        user_location = "ES"
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.id == request.user_id).first()
            if user:
                user_location = user.location

        items_dict = [item.model_dump() for item in request.items]
        result = LogisticsService.calculate_cart(items_dict, user_location)
        return result
    except Exception as e:
        logger.error(f"Error calculating cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))
