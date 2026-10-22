from datetime import datetime, timedelta, timezone
import time

import jwt
from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from src.core.config import settings
from src.core.security import SecurityShield
from src.domain.models import AuthorizedDeviceModel, ScraperStatusModel, UserModel
from src.infrastructure.database_cloud import SessionCloud

# ─── JWT helpers & In-Memory Auth Cache ──────────────────────────────────────

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
_USER_AUTH_CACHE_TTL = 60.0
_user_auth_cache: dict[int, tuple[float, UserModel]] = {}


def invalidate_user_auth_cache(user_id: int | None = None) -> None:
    if user_id is None:
        _user_auth_cache.clear()
    else:
        _user_auth_cache.pop(user_id, None)


def _fetch_active_user_cached(user_id: int) -> UserModel | None:
    now = time.monotonic()
    cached = _user_auth_cache.get(user_id)
    if cached is not None and cached[0] > now:
        return cached[1]

    try:
        with SessionCloud() as db:
            user = (
                db.query(UserModel)
                .filter(UserModel.id == user_id, UserModel.is_active == True)  # noqa: E712
                .first()
            )
            if user:
                # Access scalar fields before expunging so they stay loaded in memory
                _ = (
                    user.id,
                    user.username,
                    user.email,
                    user.role,
                    user.is_active,
                    user.location,
                    user.is_public_showcase,
                    user.pc_image_path,
                    user.mobile_image_path,
                )
                db.expunge(user)
                _user_auth_cache[user_id] = (now + _USER_AUTH_CACHE_TTL, user)
                return user
    except Exception as e:
        logger.warning(f"Error consultando usuario en Cloud DB: {e}")

    try:
        from src.infrastructure.database import SessionLocal
        with SessionLocal() as db:
            user = (
                db.query(UserModel)
                .filter(UserModel.id == user_id, UserModel.is_active == True)  # noqa: E712
                .first()
            )
            if user:
                _ = (
                    user.id,
                    user.username,
                    user.email,
                    user.role,
                    user.is_active,
                    user.location,
                    user.is_public_showcase,
                    user.pc_image_path,
                    user.mobile_image_path,
                )
                db.expunge(user)
                _user_auth_cache[user_id] = (now + _USER_AUTH_CACHE_TTL, user)
                return user
    except Exception as e:
        logger.error(f"Error consultando usuario en Local DB: {e}")

    return None


def _user_from_token(token: str | None) -> UserModel | None:
    """Decodifica un JWT y devuelve el usuario activo, o None si es inválido."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None

    return _fetch_active_user_cached(user_id)


def _is_service_key(x_api_key: str | None) -> bool:
    """True solo si la cabecera coincide con la API key servidor-a-servidor."""
    return bool(x_api_key) and x_api_key == settings.ORACULO_API_KEY


# ─── Admin helpers & guard ───────────────────────────────────────────────────

def is_admin(user: UserModel | None) -> bool:
    """Valida si un usuario posee privilegios de administración/Arquitecto."""
    if not user:
        return False
    role = (user.role or "").strip().lower()
    username = (user.username or "").strip().lower()
    email = (user.email or "").strip().lower()
    sovereign_email = (settings.SOVEREIGN_EMAIL or "").strip().lower()

    return (
        role == "admin"
        or username in ("david", "admin")
        or (bool(sovereign_email) and email == sovereign_email)
    )


def verify_api_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
    token: str = Depends(_oauth2_scheme),
):
    """
    Guardián de administración (modo dual):
      - Acepta la API key SERVIDOR-A-SERVIDOR (scrapers/workers), o
      - un JWT válido cuyo usuario tenga privilegios de administrador.
    La API key ya NO viaja en el navegador; el panel usa JWT de admin.
    """
    if _is_service_key(x_api_key):
        return "service"
    user = _user_from_token(token)
    if user and is_admin(user):
        return user
    raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador.")


# ─── Device Auth (Ojo de Sauron) ─────────────────────────────────────────────
# Nota (Fase AAA-1): el auto-registro por API key se eliminó. La API key ya no
# llega al navegador, así que autorizar dispositivos "porque traen la key" dejó
# de tener sentido — ahora el dispositivo se autoriza únicamente por el flujo
# manual de aprobación (SecurityShield.check_access / authorize_device).

def verify_device(
    request: Request,
    x_device_id: str = Header(None, alias="X-Device-ID"),
    x_device_name: str = Header("Desconocido", alias="X-Device-Name"),
):
    if not x_device_id:
        raise HTTPException(
            status_code=403,
            detail="X-Device-ID header missing. Access Denied by 3OX Shield.",
        )

    cached_access = SecurityShield.get_cached_device_access(x_device_id)
    if cached_access is not None:
        if not cached_access:
            raise HTTPException(
                status_code=403,
                detail="Dispositivo no autorizado. El Gran Arquitecto ha sido notificado.",
            )
        return x_device_id

    with SessionCloud() as db:
        ip_address = request.client.host if request.client else "Unknown IP"
        is_authorized = SecurityShield.check_access_sync(
            x_device_id, x_device_name, ip_address, db
        )

        if not is_authorized:
            raise HTTPException(
                status_code=403,
                detail="Dispositivo no autorizado. El Gran Arquitecto ha sido notificado.",
            )
    return x_device_id


# ─── Wallapop import guard (Fase AAA-3d) ──────────────────────────────────────
# POST /api/wallapop/import tiene dos llamantes legítimos con mecanismos de
# auth distintos: la extensión de Chrome (sin sesión, necesita una clave
# propia y de bajo privilegio) y la SPA ya logueada (import manual por texto
# en Purgatory, que ya manda X-Device-ID/JWT vía el interceptor de axios).
# Dual, igual que verify_api_key: acepta la clave de extensión, o si no,
# reutiliza el flujo normal de verify_device.
def verify_wallapop_import(
    request: Request,
    x_extension_key: str = Header(None, alias="X-Extension-Key"),
    x_device_id: str = Header(None, alias="X-Device-ID"),
    x_device_name: str = Header("Desconocido", alias="X-Device-Name"),
):
    if x_extension_key and x_extension_key == settings.EXTENSION_API_KEY:
        return "extension"
    return verify_device(request=request, x_device_id=x_device_id, x_device_name=x_device_name)


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

    user = _fetch_active_user_cached(user_id)
    if user:
        return user

    raise HTTPException(status_code=401, detail="Usuario no encontrado.")


def require_admin(user: UserModel = Depends(get_current_user)) -> UserModel:
    """Exige que el usuario autenticado por JWT tenga privilegios de administrador."""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador.")
    return user


# ─── Identity scoping (Fase AAA-2.1) ──────────────────────────────────────────
# Helper compartido por todos los routers que exponen un `user_id` de query o
# de body (colección, ajustes de usuario, logística...). Antes de la Fase AAA-1
# esos endpoints confiaban ciegamente en el user_id recibido del cliente
# (IDOR). Ahora cualquier usuario autenticado solo puede actuar sobre su
# propio id; solo un admin puede seguir operando sobre cualquier user_id
# (necesario para el cambio de identidad entre 'héroes' del panel).


def scope_user_id(current_user: UserModel, requested_user_id: int) -> int:
    """Devuelve requested_user_id tal cual si el usuario es admin; si no, fuerza current_user.id."""
    if is_admin(current_user):
        return requested_user_id
    return current_user.id


# ─── Startup & Unified Spider Registry ────────────────────────────────────────

REGISTERED_SPIDERS = [
    "Fantasia Personajes", "Frikiverso", "Frikimaz", "Electropolis",
    "Pixelatoy", "Amazon.es", "DeToyboys", "Ebay.es",
    "Vinted", "Wallapop", "ToymiEU", "Time4ActionToysDE",
    "BigBadToyStore", "DVDStoreSpain", "Triguetech",
    "LaMansionDelTerror", "SmythsToys", "Bixoto",
]

CANONICAL_SPIDER_NAMES = {
    "fantasia": "Fantasia Personajes",
    "fantasia personajes": "Fantasia Personajes",
    "frikiverso": "Frikiverso",
    "frikimaz": "Frikimaz",
    "electropolis": "Electropolis",
    "pixelatoy": "Pixelatoy",
    "amazon": "Amazon.es",
    "amazon.es": "Amazon.es",
    "detoyboys": "DeToyboys",
    "ebay": "Ebay.es",
    "ebay.es": "Ebay.es",
    "vinted": "Vinted",
    "wallapop": "Wallapop",
    "wallapopmanual": "Wallapop",
    "wallamanual": "Wallapop",
    "toymieu": "ToymiEU",
    "time4actiontoysde": "Time4ActionToysDE",
    "bigbadtoystore": "BigBadToyStore",
    "smythstoys": "SmythsToys",
    "dvdstorespain": "DVDStoreSpain",
    "triguetech": "Triguetech",
    "lamansiondelterror": "LaMansionDelTerror",
    "bixoto": "Bixoto",
    "all": "all",
}


def ensure_scrapers_registered():
    spiders_to_check = REGISTERED_SPIDERS

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    # 1. Registro en Supabase (Cloud) — 1 query en lote en lugar de 18 queries secuenciales
    with SessionCloud() as db:
        try:
            existing_rows = db.query(ScraperStatusModel.spider_name).all()
            existing_lower = {(r[0] or "").lower() for r in existing_rows}
            for name in spiders_to_check:
                if name.lower() not in existing_lower:
                    logger.info(f"🆕 Registrando nuevo scraper en Cloud: {name}")
                    db.add(ScraperStatusModel(
                        spider_name=name,
                        status="stopped",
                        items_scraped=0,
                        progress=0,
                        total_items_estimated=0,
                        start_time=now_utc,
                        last_update=now_utc
                    ))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to register scrapers in Cloud: {e}")

    # 2. Registro en SQLite Local (oraculo.db) — 1 query en lote
    try:
        from src.infrastructure.database import SessionLocal
        with SessionLocal() as db_loc:
            existing_rows = db_loc.query(ScraperStatusModel.spider_name).all()
            existing_lower = {(r[0] or "").lower() for r in existing_rows}
            for name in spiders_to_check:
                if name.lower() not in existing_lower:
                    logger.info(f"🆕 Registrando nuevo scraper en SQLite local: {name}")
                    db_loc.add(ScraperStatusModel(
                        spider_name=name,
                        status="stopped",
                        items_scraped=0,
                        progress=0,
                        total_items_estimated=0,
                        start_time=now_utc,
                        last_update=now_utc
                    ))
            db_loc.commit()
    except Exception as e:
        logger.error(f"Failed to register scrapers in Local SQLite: {e}")
