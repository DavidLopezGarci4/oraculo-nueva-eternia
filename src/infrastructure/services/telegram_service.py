import httpx
import logging
import json
from datetime import datetime
from pathlib import Path
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

    def log_telemetry(self, event_type: str, payload: dict):
        """Guarda eventos de telemetría de forma atómica en data/telegram_telemetry.json."""
        telemetry_file = Path("data/telegram_telemetry.json")
        try:
            telemetry_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event_type,
                "payload": payload
            }
            
            data = []
            if telemetry_file.exists():
                try:
                    with open(telemetry_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            data = json.loads(content)
                except Exception:
                    pass
            
            data.append(log_entry)
            data = data[-1000:] # Límite de 1000 registros para evitar crecimiento infinito
            
            with open(telemetry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error escribiendo telemetría de Telegram: {e}")

    async def send_message(self, text: str, chat_id: Optional[str] = None):
        """Envia un mensaje de texto plano."""
        if not self.enabled:
            return
            
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            return
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()
                # Registrar telemetría
                self.log_telemetry("MESSAGE_SENT", {"chat_id": target_chat_id, "text_preview": text[:100]})
                return response.json()
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram: {e}")
            self.log_telemetry("MESSAGE_FAILED", {"chat_id": target_chat_id, "error": str(e)})
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

    async def send_new_purgatory_vintage_alert(self, scraped_name: str, price: float, shop_name: str, url: str):
        """Alerta de nuevo lote Vintage enviado al Purgatorio para revisión del admin."""
        if not self.enabled:
            return

        message = (
            f"<b>🏺 NUEVO CANDIDATO VINTAGE EN PURGATORIO</b>\n\n"
            f"📦 <b>Producto:</b> {scraped_name}\n"
            f"💰 <b>Precio:</b> {price:.2f}€\n"
            f"🏪 <b>Tienda:</b> {shop_name}\n\n"
            f"🔗 <a href='{url}'>Ver Ficha en Web</a>"
        )
        
        return await self.send_message(message)

    async def send_wishlist_alert(self, chat_id: str, product_name: str, price: float, shop_name: str, url: str):
        """Alerta personalizada de lista de deseos para un Guardián."""
        if not self.enabled:
            return

        message = (
            f"<b>⭐ ¡FIGURA DE TU LISTA DE DESEOS ENCONTRADA!</b>\n\n"
            f"📦 <b>Producto deseado:</b> {product_name}\n"
            f"💰 <b>Precio:</b> {price:.2f}€\n"
            f"🏪 <b>Tienda:</b> {shop_name}\n\n"
            f"🔥 <i>¡Esta figura está en tu radar de deseos!</i>\n\n"
            f"🔗 <a href='{url}'>Ir a comprar ahora</a>"
        )
        
        return await self.send_message(message, chat_id=chat_id)

    async def send_price_alert(self, chat_id: str, product_name: str, price: float, target_price: float, shop_name: str, url: str):
        """Alerta de precio objetivo alcanzado."""
        if not self.enabled:
            return

        message = (
            f"<b>🎯 ALERTA DE PRECIO OBJETIVO ALCANZADO</b>\n\n"
            f"📦 <b>Producto:</b> {product_name}\n"
            f"📉 <b>Precio encontrado:</b> {price:.2f}€\n"
            f"💵 <b>Tu objetivo:</b> {target_price:.2f}€\n"
            f"🏪 <b>Tienda:</b> {shop_name}\n\n"
            f"🔗 <a href='{url}'>Ir a comprar ahora</a>"
        )
        
        return await self.send_message(message, chat_id=chat_id)

# Instancia unica para toda la app
telegram_service = TelegramService()
