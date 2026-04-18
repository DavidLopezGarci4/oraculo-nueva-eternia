import asyncio
import json
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from loguru import logger
from sqlalchemy import desc, func, or_

from src.core.security import SecurityShield
from src.domain.models import (
    AuthorizedDeviceModel,
    CollectionItemModel,
    OfferModel,
    PendingMatchModel,
    UserModel,
)
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key
from src.interfaces.api.schemas import (
    AnomalyValidationRequest,
    CreateUserRequest,
    HeroOutput,
    UserRoleUpdateRequest,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/users/create")
async def create_user(request: CreateUserRequest, x_api_key: str = Depends(verify_api_key)):
    with SessionCloud() as db:
        exists = db.query(UserModel).filter(
            or_(UserModel.email == request.email, UserModel.username == request.username)
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="El usuario o email ya existe.")

        new_user = UserModel(
            username=request.username,
            email=request.email,
            hashed_password=SecurityShield.hash_password(request.password),
            role=request.role,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"👤 Nuevo Guardián creado: {new_user.username} ({new_user.role})")
        return {"status": "success", "message": f"Héroe {new_user.username} registrado."}


@router.get("/users", response_model=List[HeroOutput], dependencies=[Depends(verify_api_key)])
async def get_all_heroes():
    with SessionCloud() as db:
        counts = db.query(
            CollectionItemModel.owner_id,
            func.count(CollectionItemModel.id).label("item_count"),
        ).group_by(CollectionItemModel.owner_id).subquery()

        users = db.query(
            UserModel,
            func.coalesce(counts.c.item_count, 0).label("collection_size"),
        ).outerjoin(counts, UserModel.id == counts.c.owner_id).all()

        results = []
        for user, count in users:
            results.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "location": user.location,
                "collection_size": count,
            })
        return results


@router.patch("/users/{user_id}/role", dependencies=[Depends(verify_api_key)])
async def update_hero_role(user_id: int, request: UserRoleUpdateRequest):
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Héroe no encontrado")

        user.role = request.role
        db.commit()
        return {"status": "success", "message": f"Rango de {user.username} actualizado a {request.role}"}


@router.post("/users/{user_id}/reset-password", dependencies=[Depends(verify_api_key)])
async def reset_hero_password(user_id: int):
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Héroe no encontrado")

        logger.warning(f"🛡️ PROTOCOLO DE RESETEO: Solicitud de cambio de contraseña para {user.username} ({user.email})")
        return {"status": "success", "message": f"Protocolo de reseteo iniciado para {user.email}"}


@router.delete("/users/{user_id}", dependencies=[Depends(verify_api_key)])
async def delete_hero(user_id: int):
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Héroe no encontrado")

        if user.role == "admin":
            raise HTTPException(status_code=403, detail="No se puede eliminar a un Arquitecto del sistema.")

        db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == user.id).delete()

        username = user.username
        db.delete(user)
        db.commit()

        logger.warning(f"🗑️ Héroe Eliminado: '{username}' (ID: {user_id}) ha sido borrado por el Arquitecto.")
        return {"status": "success", "message": f"Justicia del Arquitecto: El héroe '{username}' ha sido purgado de los registros."}


@router.get("/duplicates", dependencies=[Depends(verify_api_key)])
async def get_duplicates():
    from src.domain.models import ProductModel

    with SessionCloud() as db:
        products = db.query(ProductModel).all()
        duplicates = []

        ean_map = {}
        for p in products:
            if p.ean:
                product_info = {
                    "id": p.id,
                    "name": p.name,
                    "image_url": p.image_url,
                    "sub_category": p.sub_category,
                    "figure_id": p.figure_id,
                }
                if p.ean in ean_map:
                    ean_map[p.ean].append(product_info)
                else:
                    ean_map[p.ean] = [product_info]

        for ean, prods in ean_map.items():
            if len(prods) > 1:
                duplicates.append({"reason": f"EAN compartido: {ean}", "products": prods})

        return duplicates


@router.post("/nexus/sync", dependencies=[Depends(verify_api_key)])
async def sync_nexus(background_tasks: BackgroundTasks):
    try:
        from src.application.services.nexus_service import NexusService

        background_tasks.add_task(NexusService.sync_catalog)
        return {"status": "success", "message": "Iniciando sincronización del Nexo Maestro en segundo plano..."}
    except Exception as e:
        logger.error(f"Failed to start Nexus sync: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"No se pudo iniciar Nexus: {str(e)}")


@router.post("/validate-anomaly", dependencies=[Depends(verify_api_key)])
async def validate_anomaly(request: AnomalyValidationRequest):
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado en el Purgatorio")

        if request.action == "validate":
            item.validation_status = "VALIDATED"
            item.is_blocked = False
            item.anomaly_flags = None
            message = "Anomalía aceptada por el Arquitecto. Item desbloqueado."
        else:
            item.validation_status = "REJECTED"
            item.is_blocked = True
            message = "Item bloqueado definitivamente."

        db.commit()
        return {"status": "success", "message": message}


@router.post("/reset-smartmatches", dependencies=[Depends(verify_api_key)])
async def reset_smartmatches():
    with SessionCloud() as db:
        all_offers = db.query(OfferModel).filter(OfferModel.product_id.isnot(None)).all()

        reverted_count = 0
        for offer in all_offers:
            exists = db.query(PendingMatchModel).filter(PendingMatchModel.url == offer.url).first()
            if not exists:
                product_name = offer.product.name if offer.product else "Unknown"

                pending = PendingMatchModel(
                    scraped_name=product_name,
                    price=offer.price,
                    currency=offer.currency,
                    url=offer.url,
                    shop_name=offer.shop_name,
                    image_url=None,
                )
                db.add(pending)

            db.delete(offer)
            reverted_count += 1

        db.commit()
        return {
            "status": "success",
            "message": f"Purificación TOTAL completada. {reverted_count} ofertas devueltas al Purgatorio.",
        }


@router.get("/devices", dependencies=[Depends(verify_api_key)])
async def get_all_devices():
    with SessionCloud() as db:
        devices = db.query(AuthorizedDeviceModel).order_by(desc(AuthorizedDeviceModel.created_at)).all()
        return devices


@router.post("/devices/{device_id}/authorize", dependencies=[Depends(verify_api_key)])
async def authorize_device(device_id: str):
    with SessionCloud() as db:
        success = SecurityShield.authorize_device(device_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

        alert_msg = f"✅ *ORÁCULO INFORMA*\n\nEl dispositivo `{device_id}` ha sido **AUTORIZADO** con éxito."
        asyncio.create_task(SecurityShield.send_telegram_alert(alert_msg))

        return {"status": "success", "message": f"Dispositivo {device_id} autorizado."}


@router.delete("/devices/{device_id}", dependencies=[Depends(verify_api_key)])
async def revoke_device(device_id: str):
    with SessionCloud() as db:
        device = db.query(AuthorizedDeviceModel).filter(
            AuthorizedDeviceModel.device_id == device_id
        ).first()
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

        db.delete(device)
        db.commit()
        return {"status": "success", "message": f"Acceso revocado para {device_id}."}
