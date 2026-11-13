import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from loguru import logger
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from src.core.config import settings
from src.core.rate_limit import rate_limit
from src.core.security import SecurityShield
from src.domain.models import UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.infrastructure.email_service import EmailService
from src.interfaces.api.deps import (
    create_access_token,
    invalidate_user_auth_cache,
    is_admin,
    require_admin,
)
from src.interfaces.api.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    StatusMessageOutput,
    ForgotPasswordOutput,
    LoginOutput,
    UserMinimalOutput,
)
from typing import List

router = APIRouter(prefix="/api/auth", tags=["auth"])

_RESERVED_USERNAMES = frozenset(
    {
        "admin",
        "administrator",
        "root",
        "system",
        "superadmin",
        "david",
        "arquitecto",
        "moderator",
        "support",
    }
)


def _hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256((raw_token or "").strip().encode("utf-8")).hexdigest()


@router.post("/register", response_model=StatusMessageOutput, dependencies=[Depends(rate_limit(5, 300, "register"))])
def register(request: RegisterRequest):
    """
    Fase de Reclutamiento: Permite a nuevos usuarios unirse como Guardianes con nombre propio.
    """
    clean_username = (request.username or "").strip()
    clean_email = (request.email or "").strip().lower()
    if len(clean_username) < 2 or clean_username.lower() in _RESERVED_USERNAMES:
        raise HTTPException(
            status_code=400,
            detail="Nombre de héroe no permitido o reservado.",
        )

    with SessionCloud() as db:
        exists = (
            db.query(UserModel)
            .filter(
                or_(
                    func.lower(UserModel.email) == clean_email,
                    func.lower(UserModel.username) == clean_username.lower(),
                )
            )
            .first()
        )
        if exists:
            raise HTTPException(
                status_code=400,
                detail="Este nombre de héroe o email ya existe en el Oráculo.",
            )

        new_user = UserModel(
            username=clean_username,
            email=clean_email,
            hashed_password=SecurityShield.hash_password(request.password),
            role="viewer",
        )
        db.add(new_user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Este nombre de héroe o email ya existe en el Oráculo.",
            )
        db.refresh(new_user)

        logger.info(f"👤 Nuevo Héroe Reclutado: {new_user.username} ({new_user.role})")
        return {
            "status": "success",
            "message": "¡Héroe reclutado con éxito! Ahora puedes entrar.",
        }


@router.post("/forgot-password", response_model=ForgotPasswordOutput, dependencies=[Depends(rate_limit(3, 300, "forgot-password"))])
def forgot_password(
    request: ForgotPasswordRequest, background_tasks: BackgroundTasks
):
    """
    Fase 15: Genera un token de reseteo y lo envía por correo (almacenado hasheado con SHA-256).
    """
    clean_email = (request.email or "").strip().lower()
    with SessionCloud() as db:
        user = db.query(UserModel).filter(func.lower(UserModel.email) == clean_email).first()
        if not user or not user.is_active:
            # Por seguridad, no decimos si el email existe o no
            return {
                "status": "success",
                "message": "Si el correo es correcto, recibirás un enlace de recuperación.",
            }

        token = secrets.token_urlsafe(32)
        user.reset_token = _hash_reset_token(token)
        user.reset_token_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        db.commit()

        background_tasks.add_task(
            EmailService.send_reset_email, user.email, user.username, token
        )

        return {
            "status": "success",
            "message": "Enlace enviado. Revisa tu correo (y el SPAM).",
            "debug_token": token if settings.DEBUG else None,
        }


@router.post("/reset-password", response_model=StatusMessageOutput, dependencies=[Depends(rate_limit(5, 300, "reset-password"))])
def reset_password(request: ResetPasswordRequest):
    """
    Fase 15: Valida el token (comparando hash SHA-256) y cambia la contraseña.
    """
    token_hash = _hash_reset_token(request.token)
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    with SessionCloud() as db:
        user = (
            db.query(UserModel)
            .filter(
                UserModel.reset_token == token_hash,
                UserModel.reset_token_expiry > now_utc,
            )
            .first()
        )

        if not user or not user.is_active:
            raise HTTPException(
                status_code=400, detail="El token es inválido o ha caducado."
            )

        user.hashed_password = SecurityShield.hash_password(request.new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        invalidate_user_auth_cache(user.id)

        logger.info(f"🔑 Contraseña reseteada para: {user.username}")
        return {
            "status": "success",
            "message": "Tu llave ha sido renovada. Ya puedes entrar al Oráculo.",
        }


@router.post("/login", response_model=LoginOutput, dependencies=[Depends(rate_limit(10, 300, "login"))])
def login(request: LoginRequest):
    """
    Autenticación de Héroes y Guardianes. Valida email y contraseña (PBKDF2).
    Respuesta uniforme ante credenciales inválidas para prevenir enumeración de emails.
    """
    clean_email = (request.email or "").strip().lower()
    with SessionCloud() as db:
        is_sovereign_email = False
        if (
            settings.SOVEREIGN_EMAIL
            and clean_email == settings.SOVEREIGN_EMAIL.lower().strip()
        ):
            is_sovereign_email = True
            logger.info("🛡️ Intento de acceso de IDENTIDAD SOBERANA detectado.")

        user = db.query(UserModel).filter(func.lower(UserModel.email) == clean_email).first()

        if not user or not user.is_active:
            # Ejecutar verificación ficticia para igualar coste temporal frente a ataques de timing
            SecurityShield.verify_password(
                request.password,
                "00" * 48,
            )
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

        is_valid = SecurityShield.verify_password(
            request.password, user.hashed_password
        )

        if not is_valid:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

        if is_sovereign_email and is_valid:
            master_admin = (
                db.query(UserModel).filter(UserModel.role == "admin", UserModel.is_active == True).first()  # noqa: E712
            )
            if master_admin:
                logger.warning(
                    f"👑 Alias Activado: {user.username} asume el control del Arquitecto ({master_admin.username})"
                )
                user = master_admin

        return {
            "status": "success",
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
            "access_token": create_access_token(user.id, user.role),
            "token_type": "bearer",
            "is_sovereign": is_admin(user),
        }


@router.get("/users", response_model=List[UserMinimalOutput])
def get_users_minimal(_admin: UserModel = Depends(require_admin)):
    """Retorna la lista de usuarios para el selector rápido. Solo administradores (Fase AAA-1.8)."""
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
