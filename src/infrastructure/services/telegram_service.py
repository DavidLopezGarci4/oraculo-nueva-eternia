import httpx
import logging
from typing import Optional
from src.core.config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    """
    Servicio para el envio de notificaciones a Telegram.
    Fase 8.5: El Ojo de Sauron.
    """
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)
        
        if not self.enabled:
            logger.warning("TelegramService: No se han configurado las claves (TOKEN/CHAT_ID). Las alertas estaran desactivadas.")

    async def send_message(self, text: str):
        """Envia un mensaje de texto plano."""
        if not self.enabled:
            return
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram: {e}")
            return None

    async def send_deal_alert(self, product_name: str, price: float, shop_name: str, url: str):
        """Envia una alerta de oferta detectada."""
        if not self.enabled:
            return

        message = (
            f"<b>👁️ EL OJO DE SAURON DETECTA UN HALLAZGO</b>\n\n"
            f"📦 <b>Producto:</b> {product_name}\n"
            f"💰 <b>Precio:</b> {price:.2f}€\n"
            f"🏪 <b>Tienda:</b> {shop_name}\n\n"
            f"🔗 <a href='{url}'>Ver Oferta en la Web</a>"
        )
        
        return await self.send_message(message)

    async def send_mandatory_buy_alert(self, product_name: str, price: float, landed_price: float, score: int, shop_name: str, url: str):
        """Alerta de ALTA PRIORIDAD para oportunidades de 90+ puntos."""
        if not self.enabled:
            return

        message = (
            f"<b>🚨 COMPRA OBLIGATORIA DETECTADA 🚨</b>\n\n"
            f"🌟 <b>Opportunity Score:</b> {score}/100\n"
            f"📦 <b>Producto:</b> {product_name}\n"
            f"🏷️ <b>Precio Tienda:</b> {price:.2f}€\n"
            f"🛬 <b>Landed Price:</b> {landed_price:.2f}€\n"
            f"🏪 <b>Tienda:</b> {shop_name}\n\n"
            f"🔥 <i>Esta oferta ha superado el análisis de inversión del Oráculo.</i>\n\n"
            f"🔗 <a href='{url}'>IR A LA WEB AHORA</a>"
        )
        
        return await self.send_message(message)

# Instancia unica para toda la app
telegram_service = TelegramService()
