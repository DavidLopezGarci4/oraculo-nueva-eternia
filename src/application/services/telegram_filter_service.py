import logging
from typing import Optional
from sqlalchemy.orm import Session
from src.domain.models import SystemConfigModel, UserModel, CollectionItemModel

logger = logging.getLogger(__name__)

CONFIG_KEY = "telegram_alert_only_missing"

def is_telegram_only_missing_enabled(db: Session) -> bool:
    """
    Comprueba si está activo el filtro para alertar por Telegram solo
    figuras que el usuario NO tenga ya en su colección. Por defecto es True.
    """
    try:
        cfg = db.query(SystemConfigModel).filter(SystemConfigModel.key == CONFIG_KEY).first()
        if cfg is None:
            return True
        return cfg.value.strip().lower() in ("true", "1", "yes", "si")
    except Exception as e:
        logger.error(f"Error leyendo configuración '{CONFIG_KEY}': {e}")
        return True

def set_telegram_only_missing_enabled(db: Session, enabled: bool) -> bool:
    """
    Actualiza la preferencia del filtro de figuras poseídas en Telegram.
    """
    try:
        cfg = db.query(SystemConfigModel).filter(SystemConfigModel.key == CONFIG_KEY).first()
        if not cfg:
            cfg = SystemConfigModel(key=CONFIG_KEY, value=str(enabled).lower())
            db.add(cfg)
        else:
            cfg.value = str(enabled).lower()
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error guardando configuración '{CONFIG_KEY}': {e}")
        db.rollback()
        return False

def should_send_product_push(db: Session, product_id: int, chat_id: Optional[str] = None) -> bool:
    """
    Determina si se debe despachar una alerta push a Telegram para un determinado producto.
    Si el filtro está activado y el usuario ya posee la figura (acquired == True), devuelve False.
    """
    if not is_telegram_only_missing_enabled(db):
        return True

    try:
        # 1. Determinar el usuario objetivo (por chat_id o admin por defecto)
        target_user = None
        if chat_id:
            target_user = db.query(UserModel).filter(
                UserModel.telegram_chat_id == str(chat_id),
                UserModel.is_active == True
            ).first()

        if not target_user:
            # Fallback al usuario principal / admin
            target_user = db.query(UserModel).filter(
                (UserModel.role == "admin") | (UserModel.username.ilike("david")),
                UserModel.is_active == True
            ).first()

        if not target_user:
            return True

        # 2. Comprobar si ya dispone de la figura en su Fortaleza (acquired == True)
        owned_item = db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == target_user.id,
            CollectionItemModel.product_id == product_id,
            CollectionItemModel.acquired == True
        ).first()

        if owned_item:
            logger.info(
                f"🛡️ Telegram Push filtrado: Producto ID {product_id} ya figura como ADQUIRIDO "
                f"en la Fortaleza de {target_user.username}. Notificación push omitida."
            )
            return False

        return True
    except Exception as e:
        logger.error(f"Error comprobando inventario para push Telegram (producto {product_id}): {e}")
        return True
