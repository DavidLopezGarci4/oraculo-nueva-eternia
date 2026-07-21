from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from src.core.config import settings
from src.core.security import SecurityShield
from src.domain.models import AuthorizedDeviceModel, ScraperStatusModel, UserModel
from src.infrastructure.database_cloud import SessionCloud

# ─── JWT helpers (compartidos por todos los guardianes) ───────────────────────

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _user_from_token(token: str | None) -> UserModel | None:
    """Decodifica un JWT y devuelve el usuario activo, o None si es inválido."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
    with SessionCloud() as db:
        return (
            db.query(UserModel)
            .filter(UserModel.id == user_id, UserModel.is_active == True)  # noqa: E712
            .first()
        )


def _is_service_key(x_api_key: str | None) -> bool:
    """True solo si la cabecera coincide con la API key servidor-a-servidor."""
    return bool(x_api_key) and x_api_key == settings.ORACULO_API_KEY


# ─── Admin guard (antes: verify_api_key) ──────────────────────────────────────

def verify_api_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
    token: str = Depends(_oauth2_scheme),
):
    """
    Guardián de administración (modo dual):
      - Acepta la API key SERVIDOR-A-SERVIDOR (scrapers/workers), o
      - un JWT válido cuyo usuario tenga rol 'admin'.
    La API key ya NO viaja en el navegador; el panel usa JWT de admin.
    """
    if _is_service_key(x_api_key):
        return "service"
    user = _user_from_token(token)
    if user and user.role == "admin":
        return user
    raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador.")


# ─── Device Auth (Ojo de Sauron) ─────────────────────────────────────────────
# Nota (Fase AAA-1): el auto-registro por API key se eliminó. La API key ya no
# llega al navegador, así que autorizar dispositivos "porque traen la key" dejó
# de tener sentido — ahora el dispositivo se autoriza únicamente por el flujo
# manual de aprobación (SecurityShield.check_access / authorize_device).

async def verify_device(
    request: Request,
    x_device_id: str = Header(None, alias="X-Device-ID"),
    x_device_name: str = Header("Desconocido", alias="X-Device-Name"),
):
    if not x_device_id:
        raise HTTPException(
            status_code=403,
            detail="X-Device-ID header missing. Access Denied by 3OX Shield.",
        )

    with SessionCloud() as db:
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

def create_access_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_user(token: str = Depends(_oauth2_scheme)) -> UserModel:
    """
    Autenticación exclusivamente por JWT (Fase AAA-1: se retiró el bypass de
    administración por API Key — esa key es ahora solo servidor-a-servidor).
    """
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
        user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()  # noqa: E712
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado.")
        return user


def require_admin(user: UserModel = Depends(get_current_user)) -> UserModel:
    """Exige que el usuario autenticado por JWT tenga rol admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador.")
    return user


# ─── Identity scoping (Fase AAA-2.1) ──────────────────────────────────────────
# Helper compartido por todos los routers que exponen un `user_id` de query o
# de body (colección, ajustes de usuario, logística...). Antes de la Fase AAA-1
# esos endpoints confiaban ciegamente en el user_id recibido del cliente
# (IDOR). Ahora cualquier usuario autenticado solo puede actuar sobre su
# propio id; solo un admin puede seguir operando sobre cualquier user_id
# (necesario para el cambio de identidad entre 'héroes' del panel).

def is_admin(user: UserModel) -> bool:
    return user.role == "admin" or user.username == "David"


def scope_user_id(current_user: UserModel, requested_user_id: int) -> int:
    """Devuelve requested_user_id tal cual si el usuario es admin; si no, fuerza current_user.id."""
    if is_admin(current_user):
        return requested_user_id
    return current_user.id


# ─── Startup ──────────────────────────────────────────────────────────────────

def ensure_scrapers_registered():
    spiders_to_check = [
        "Fantasia Personajes", "Frikiverso", "Frikimaz", "Electropolis",
        "Pixelatoy", "Amazon.es", "DeToyboys", "Ebay.es",
        "Vinted", "Wallapop", "ToymiEU", "Time4ActionToysDE",
        "BigBadToyStore", "DVDStoreSpain", "Triguetech",
        "LaMansionDelTerror", "SmythsToys",
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
