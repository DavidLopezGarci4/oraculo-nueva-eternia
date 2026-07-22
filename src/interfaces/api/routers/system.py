import sys

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key
from src.interfaces.api.schemas import StatusMessageOutput

router = APIRouter(tags=["system"])


@router.get("/api/system/audit", dependencies=[Depends(verify_api_key)])
async def system_audit():
    import sqlalchemy

    from src.core.config import settings
    from src.domain.models import (
        AuthorizedDeviceModel,
        CollectionItemModel,
        OfferModel,
        ProductModel,
        UserModel,
    )
    from src.infrastructure.database_cloud import cloud_url, engine_cloud

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

            conn_info = (
                str(engine_cloud.url).split("@")[-1]
                if "@" in str(engine_cloud.url)
                else "local_sqlite"
            )

            security_cols = []
            try:
                col_check = db.execute(sqlalchemy.text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'users' "
                    "AND column_name IN ('reset_token', 'reset_token_expiry')"
                )).fetchall()
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
                        "PASS_LOADED": settings.SMTP_PASS is not None
                        and len(settings.SMTP_PASS) > 5,
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

import json
from src.interfaces.api.deps import get_current_user
from src.domain.models import SystemConfigModel, UserModel

@router.get("/api/system/sword-configs")
async def get_sword_configs(current_user: UserModel = Depends(get_current_user)):
    with SessionCloud() as db:
        cfg = db.query(SystemConfigModel).filter(SystemConfigModel.key == "sword_configs").first()
        if cfg:
            try:
                return json.loads(cfg.value)
            except Exception:
                return {}
        return {}

@router.post("/api/system/sword-configs", response_model=StatusMessageOutput)
async def save_sword_configs(configs: dict, current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != 2:
        raise HTTPException(status_code=403, detail="No autorizado para modificar la configuración de espadas.")
        
    with SessionCloud() as db:
        cfg = db.query(SystemConfigModel).filter(SystemConfigModel.key == "sword_configs").first()
        if not cfg:
            cfg = SystemConfigModel(key="sword_configs")
            db.add(cfg)
        cfg.value = json.dumps(configs)
        db.commit()
    return {"status": "success", "message": "Configuración de espadas guardada exitosamente."}

async def run_maintenance_task():
    from src.application.services.maintenance_service import MaintenanceService
    from src.core.security import SecurityShield
    
    logger.info("🧹 [TASK] Iniciando purificación FinOps de base de datos en segundo plano...")
    try:
        with SessionCloud() as db:
            stats = MaintenanceService.compact_database(db)
            
            # Formatear el reporte de Telegram
            msg = (
                "🧹 <b>[FinOps] Purificación del Oráculo Completada</b>\n\n"
                f"• Productos procesados: <b>{stats.get('products_processed', 0)}</b>\n"
                f"• Resúmenes mensuales guardados: <b>{stats.get('monthly_stats_saved', 0)}</b>\n"
                f"• Ofertas inactivas purgadas: <b>{stats.get('offers_purged', 0)}</b>\n"
                f"• Historial detallado purgado: <b>{stats.get('price_history_purged', 0)}</b>\n"
                f"• Logs de scrapers truncados: <b>{stats.get('logs_truncated', 0)}</b>\n"
                f"• Registros de lista negra purgados: <b>{stats.get('blacklist_purged', 0)}</b>\n\n"
                "✨ <i>¡Base de datos de Supabase saneada con éxito!</i>"
            )
            await SecurityShield.send_telegram_alert(msg)
            logger.info("🧹 [TASK] Purificación en segundo plano completada y alerta de Telegram enviada.")
    except Exception as e:
        err_msg = f"❌ <b>[FinOps] Fallo en la Purificación</b>\n\nError: <code>{str(e)}</code>"
        await SecurityShield.send_telegram_alert(err_msg)
        logger.error(f"❌ Error en la tarea de mantenimiento en segundo plano: {e}")

@router.post("/api/system/maintenance", response_model=StatusMessageOutput)
async def run_maintenance(
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user)
):
    """Ejecuta la compactación de historial de precios y mantenimiento FinOps en segundo plano."""
    if current_user.role != "admin" and current_user.id != 2:
        raise HTTPException(
            status_code=403, 
            detail="No tienes los privilegios del Arquitecto necesarios para purificar el Oráculo."
        )
        
    background_tasks.add_task(run_maintenance_task)
    return {
        "status": "success",
        "message": "Purificación FinOps del Oráculo iniciada con éxito en segundo plano. Recibirás una alerta en Telegram con el desglose del espacio liberado al finalizar."
    }
