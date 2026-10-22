import asyncio
import hashlib
import hmac
import os
import threading
import time
from datetime import datetime, timezone
from typing import Optional

import anyio
import httpx
from loguru import logger
from sqlalchemy.orm import Session

from src.core.config import settings
from src.domain.models import AuthorizedDeviceModel

_DEVICE_CACHE_TTL = 300.0  # 5 minutes
_DEVICE_LAST_ACCESS_THROTTLE = 900.0  # 15 minutes
# device_id -> (is_authorized, cache_expires_at, last_db_touch_at)
_device_cache: dict[str, tuple[bool, float, float]] = {}


class SecurityShield:
    """
    Servicio de Seguridad 3OX (Escudo de Eternia).
    Gestiona la autorización de dispositivos, hashing de contraseñas y alertas.
    """

    @staticmethod
    def invalidate_device_cache(device_id: Optional[str] = None) -> None:
        if device_id is None:
            _device_cache.clear()
        else:
            _device_cache.pop(device_id, None)

    @staticmethod
    def get_cached_device_access(device_id: str) -> Optional[bool]:
        now = time.monotonic()
        entry = _device_cache.get(device_id)
        if entry is None:
            return None
        is_authorized, expires_at, last_db_touch = entry
        if now >= expires_at or (now - last_db_touch) >= _DEVICE_LAST_ACCESS_THROTTLE:
            return None
        return is_authorized

    @staticmethod
    def hash_password(password: str) -> str:
        """Crea un hash seguro de la contraseña usando PBKDF2."""
        salt = os.urandom(16)
        pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return (salt + pw_hash).hex()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash."""
        try:
            stored_data = bytes.fromhex(hashed_password)
            salt = stored_data[:16]
            stored_hash = stored_data[16:]
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return hmac.compare_digest(stored_hash, new_hash)
        except Exception as e:
            logger.error(f"Error verificando password: {e}")
            return False

    @staticmethod
    async def send_telegram_alert(message: str, reply_markup: Optional[dict] = None, parse_mode: str = "HTML"):
        """Envía un mensaje al Gran Arquitecto vía Telegram con soporte de botones interactivos."""
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            logger.warning("⚠️ Intento de envío de alerta Telegram cancelado: Credenciales ausentes.")
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                logger.debug("🛡️ Alerta de Telegram enviada con éxito.")
        except Exception as e:
            logger.error(f"❌ Error al enviar alerta de Telegram: {e}")

    @staticmethod
    def _dispatch_telegram_alert_from_sync(message: str, reply_markup: Optional[dict] = None) -> None:
        try:
            anyio.from_thread.run(SecurityShield.send_telegram_alert, message, reply_markup)
            return
        except Exception:
            pass
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(SecurityShield.send_telegram_alert(message, reply_markup=reply_markup))
            return
        except RuntimeError:
            threading.Thread(
                target=lambda: asyncio.run(SecurityShield.send_telegram_alert(message, reply_markup=reply_markup)),
                daemon=True,
            ).start()

    @staticmethod
    def _check_access_core(
        device_id: str, device_name: str, ip_address: str, db: Session
    ) -> tuple[bool, Optional[tuple[str, dict]]]:
        now = time.monotonic()
        cached_entry = _device_cache.get(device_id)
        if cached_entry is not None:
            is_auth, expires_at, last_touch = cached_entry
            if now < expires_at and (now - last_touch) < _DEVICE_LAST_ACCESS_THROTTLE:
                return is_auth, None

        device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id == device_id).first()

        if not device:
            logger.info(f"🆕 Nuevo dispositivo detectado: {device_id} ({device_name})")
            new_device = AuthorizedDeviceModel(
                device_id=device_id,
                device_name=device_name,
                is_authorized=False,
            )
            db.add(new_device)
            db.commit()
            db.refresh(new_device)

            _device_cache[device_id] = (False, now + _DEVICE_CACHE_TTL, now)

            alert_msg = (
                f"🛡️ <b>[EL ORÁCULO: ALERTA DE ACCESO]</b>\n\n"
                f"Se ha detectado un nuevo dispositivo intentando conectar:\n"
                f"📱 <b>Dispositivo:</b> {device_name}\n"
                f"🆔 <b>ID:</b> <code>{device_id}</code>\n"
                f"🌐 <b>IP:</b> <code>{ip_address}</code>\n\n"
                f"⚠️ <b>Acceso BLOQUEADO</b> hasta que lo autorices."
            )
            device_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Permitir Acceso", "callback_data": f"device:allow:{new_device.id}"},
                        {"text": "🚫 Bloquear / Eliminar", "callback_data": f"device:deny:{new_device.id}"},
                    ]
                ]
            }
            return False, (alert_msg, device_keyboard)

        last_touch = cached_entry[2] if cached_entry is not None else 0.0
        if last_touch == 0.0 or (now - last_touch) >= _DEVICE_LAST_ACCESS_THROTTLE:
            device.last_access_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db.commit()
            last_touch = now

        is_auth = bool(device.is_authorized)
        _device_cache[device_id] = (is_auth, now + _DEVICE_CACHE_TTL, last_touch)

        if not is_auth:
            logger.warning(f"🚫 Acceso denegado para dispositivo conocido pero no autorizado: {device_id}")
            return False, None

        return True, None

    @staticmethod
    def check_access_sync(device_id: str, device_name: str, ip_address: str, db: Session) -> bool:
        is_auth, alert_payload = SecurityShield._check_access_core(device_id, device_name, ip_address, db)
        if alert_payload is not None:
            alert_msg, device_keyboard = alert_payload
            SecurityShield._dispatch_telegram_alert_from_sync(alert_msg, reply_markup=device_keyboard)
        return is_auth

    @staticmethod
    async def check_access(device_id: str, device_name: str, ip_address: str, db: Session) -> bool:
        """
        Verifica si un dispositivo tiene permiso.
        Si es nuevo, lo registra y notifica al administrador.
        """
        is_auth, alert_payload = SecurityShield._check_access_core(device_id, device_name, ip_address, db)
        if alert_payload is not None:
            alert_msg, device_keyboard = alert_payload
            await SecurityShield.send_telegram_alert(alert_msg, reply_markup=device_keyboard)
        return is_auth

    @staticmethod
    def authorize_device(device_id: str, db: Session):
        """Autoriza un dispositivo para acceso permanente."""
        device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id == device_id).first()
        if device:
            device.is_authorized = True
            db.commit()
            now = time.monotonic()
            _device_cache[device_id] = (True, now + _DEVICE_CACHE_TTL, now)
            logger.info(f"✅ Dispositivo {device_id} autorizado por el Arquitecto.")
            return True
        return False
