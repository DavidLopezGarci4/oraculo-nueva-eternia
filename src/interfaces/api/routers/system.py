import sys

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key

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
