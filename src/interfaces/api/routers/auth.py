import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from sqlalchemy import or_

from src.core.config import settings
from src.core.security import SecurityShield
from src.domain.models import UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.infrastructure.email_service import EmailService
from src.interfaces.api.deps import create_access_token
from src.interfaces.api.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(request: RegisterRequest):
    """
    Fase de Reclutamiento: Permite a nuevos usuarios unirse como Guardianes con nombre propio.
    """
    with SessionCloud() as db:
        exists = (
            db.query(UserModel)
            .filter(
                or_(
                    UserModel.email == request.email,
                    UserModel.username == request.username,
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
            username=request.username,
            email=request.email,
            hashed_password=SecurityShield.hash_password(request.password),
            role="viewer",
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"👤 Nuevo Héroe Reclutado: {new_user.username} ({new_user.role})")
        return {
            "status": "success",
            "message": "¡Héroe reclutado con éxito! Ahora puedes entrar.",
        }


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, background_tasks: BackgroundTasks
):
    """
    Fase 15: Genera un token de reseteo y lo envía por correo.
    """
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        if not user:
            # Por seguridad, no decimos si el email existe o no
            return {
                "status": "success",
                "message": "Si el correo es correcto, recibirás un enlace de recuperación.",
            }

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        background_tasks.add_task(
            EmailService.send_reset_email, user.email, user.username, token
        )

        return {
            "status": "success",
            "message": "Enlace enviado. Revisa tu correo (y el SPAM).",
            "debug_token": token if settings.DEBUG else None,
        }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Fase 15: Valida el token y cambia la contraseña.
    """
    with SessionCloud() as db:
        user = (
            db.query(UserModel)
            .filter(
                UserModel.reset_token == request.token,
                UserModel.reset_token_expiry > datetime.utcnow(),
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=400, detail="El token es inválido o ha caducado."
            )

        user.hashed_password = SecurityShield.hash_password(request.new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()

        logger.info(f"🔑 Contraseña reseteada para: {user.username}")
        return {
            "status": "success",
            "message": "Tu llave ha sido renovada. Ya puedes entrar al Oráculo.",
        }


@router.post("/login")
async def login(request: LoginRequest):
    """
    Autenticación de Héroes y Guardianes.
    Valida Email y Contraseña. Soporta X-API-Key como bypass soberano.
    """
    with SessionCloud() as db:
        # Phase 51: Sovereign Identity Bypass
        is_sovereign_email = False
        if (
            settings.SOVEREIGN_EMAIL
            and request.email.lower().strip()
            == settings.SOVEREIGN_EMAIL.lower().strip()
        ):
            is_sovereign_email = True
            logger.info("🛡️ Intento de acceso de IDENTIDAD SOBERANA detectado.")

        user = db.query(UserModel).filter(UserModel.email == request.email).first()

        is_sovereign_bypass = request.password == settings.ORACULO_API_KEY

        if not user:
            raise HTTPException(
                status_code=401, detail="Email no registrado en el Oráculo."
            )

        if is_sovereign_bypass:
            is_valid = True
            logger.info(
                f"🛡️ Acceso SOBERANO detectado por API KEY para {user.username}"
            )
        else:
            is_valid = SecurityShield.verify_password(
                request.password, user.hashed_password
            )

        if not is_valid:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

        # Si la validación fue exitosa Y es el email Mágico de Soberanía
        # Transferimos silenciosamente la sesión al usuario 'admin' maestro
        if is_sovereign_email and is_valid:
            master_admin = (
                db.query(UserModel).filter(UserModel.role == "admin").first()
            )
            if master_admin:
                logger.warning(
                    f"👑 Alias Activado: {user.username} asume el control del Arquitecto ({master_admin.username})"
                )
                user = master_admin
                is_sovereign_bypass = True

        return {
            "status": "success",
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
            "access_token": create_access_token(user.id, user.role),
            "token_type": "bearer",
            "is_sovereign": user.role == "admin" or is_sovereign_bypass,
        }


@router.get("/users")
async def get_users_minimal():
    """Retorna la lista de usuarios para el selector rápido (Modo Legacy/Test)"""
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
