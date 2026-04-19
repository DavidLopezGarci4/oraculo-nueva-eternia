from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from src.core.config import settings
from src.core.security import SecurityShield
from src.domain.models import AuthorizedDeviceModel, ScraperStatusModel, UserModel
from src.infrastructure.database_cloud import SessionCloud

# ─── API Key ─────────────────────────────────────────────────────────────────

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if x_api_key != settings.ORACULO_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key. Access Denied.")
    return x_api_key


# ─── Device Auth (Ojo de Sauron) ─────────────────────────────────────────────

async def verify_device(
    request: Request,
    x_device_id: str = Header(None, alias="X-Device-ID"),
    x_device_name: str = Header("Desconocido", alias="X-Device-Name"),
    x_api_key: str = Header(None, alias="X-API-Key"),
):
    if not x_device_id:
        raise HTTPException(
            status_code=403,
            detail="X-Device-ID header missing. Access Denied by 3OX Shield.",
        )

    with SessionCloud() as db:
        if x_api_key == settings.ORACULO_API_KEY:
            device = (
                db.query(AuthorizedDeviceModel)
                .filter(AuthorizedDeviceModel.device_id == x_device_id)
                .first()
            )
            if not device:
                device = AuthorizedDeviceModel(
                    device_id=x_device_id,
                    device_name=x_device_name,
                    is_authorized=True,
                )
                db.add(device)
            else:
                device.is_authorized = True
            db.commit()
            return x_device_id

        ip_address = request.client.host if request.client else "Unknown IP"
        is_authorized = await SecurityShield.check_access(
            x_device_id, x_device_name, ip_address, db
        )

        if not is_authorized:
            raise HTTPException(
                status_code=403,
                detail="Dispositivo no autorizado. El Gran Arquitecto ha sido notificado.",
            )
    return x_device_id


# ─── JWT ─────────────────────────────────────────────────────────────────────

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def create_access_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_user(token: str = Depends(_oauth2_scheme)) -> UserModel:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido.")

    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado.")
        return user


# ─── Startup ──────────────────────────────────────────────────────────────────

def ensure_scrapers_registered():
    spiders_to_check = [
        "Fantasia Personajes", "Frikiverso", "Frikimaz", "Electropolis",
        "Pixelatoy", "Amazon.es", "DeToyboys", "Ebay.es",
        "Vinted", "Wallapop", "ToymiEU", "Time4ActionToysDE",
        "BigBadToyStore", "Tradeinn", "DVDStoreSpain",
    ]

    with SessionCloud() as db:
        try:
            for name in spiders_to_check:
                exists = (
                    db.query(ScraperStatusModel)
                    .filter(ScraperStatusModel.spider_name.ilike(name))
                    .first()
                )
                if not exists:
                    logger.info(f"🆕 Registrando nuevo scraper en sistema: {name}")
                    db.add(ScraperStatusModel(spider_name=name, status="stopped"))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to register scrapers: {e}")
