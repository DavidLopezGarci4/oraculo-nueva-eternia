import hashlib
import hmac
import os
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
from src.core.config import settings
from src.domain.models import AuthorizedDeviceModel

class SecurityShield:
    """
    Servicio de Seguridad 3OX (Escudo de Eternia).
    Gestiona la autorización de dispositivos, hashing de contraseñas y alertas.
    """

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
    async def send_telegram_alert(message: str):
        """Envía un mensaje al Gran Arquitecto vía Telegram."""
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            logger.warning("⚠️ Intento de envío de alerta Telegram cancelado: Credenciales ausentes.")
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                logger.debug("🛡️ Alerta de Telegram enviada con éxito.")
        except Exception as e:
            logger.error(f"❌ Error al enviar alerta de Telegram: {e}")

    @staticmethod
    async def check_access(device_id: str, device_name: str, ip_address: str, db: Session) -> bool:
        """
        Verifica si un dispositivo tiene permiso. 
        Si es nuevo, lo registra y notifica al administrador.
        """
        device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id == device_id).first()
        
        if not device:
            # Nuevo dispositivo detectado - Registrar en las sombras
            logger.info(f"🆕 Nuevo dispositivo detectado: {device_id} ({device_name})")
            new_device = AuthorizedDeviceModel(
                device_id=device_id,
                device_name=device_name,
                is_authorized=False # Requiere aprobación manual
            )
            db.add(new_device)
            db.commit()
            
            # Notificar al Ojo de Sauron
            alert_msg = (
                f"🛡️ *EL ORÁCULO: ALERTA DE ACCESO*\n\n"
                f"Se ha detectado un nuevo dispositivo intentando conectar:\n"
                f"📱 *Dispositivo:* {device_name}\n"
                f"🆔 *ID:* `{device_id}`\n"
                f"🌐 *IP:* {ip_address}\n\n"
                f"⚠️ *Acceso BLOQUEADO* hasta aprobación manual en el panel de control."
            )
            await SecurityShield.send_telegram_alert(alert_msg)
            return False
            
        # El dispositivo ya es conocido
        device.last_access_at = datetime.utcnow()
        db.commit()
        
        if not device.is_authorized:
            logger.warning(f"🚫 Acceso denegado para dispositivo conocido pero no autorizado: {device_id}")
            return False
            
        return True

    @staticmethod
    def authorize_device(device_id: str, db: Session):
        """Autoriza un dispositivo para acceso permanente."""
        device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id == device_id).first()
        if device:
            device.is_authorized = True
            db.commit()
            logger.info(f"✅ Dispositivo {device_id} autorizado por el Arquitecto.")
            return True
        return False
