import asyncio
import hmac
import html
import httpx
import logging
import os
import re
from typing import Optional
from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel, ScraperStatusModel, PendingMatchModel, OfferModel, ProductModel, AuthorizedDeviceModel
from src.interfaces.api.routers.scrapers import run_scraper_task, stop_scrapers
from src.infrastructure.services.telegram_service import telegram_service

logger = logging.getLogger(__name__)

class TelegramListener:
    """
    Escucha y procesa comandos de Telegram en segundo plano mediante Long Polling.
    """
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.admin_chat_id = settings.TELEGRAM_CHAT_ID
        self.enabled = bool(self.token)
        self.offset = 0
        self.running = False
        
        if not self.enabled:
            logger.warning("TelegramListener: No se ha configurado TELEGRAM_BOT_TOKEN. La escucha de comandos estará inactiva.")

    def is_sovereign_admin(self, chat_id: int) -> bool:
        """Determina si el chat_id corresponde única y exclusivamente al Gran Arquitecto / Soberano."""
        chat_id_str = str(chat_id)
        if self.admin_chat_id and chat_id_str == str(self.admin_chat_id):
            return True
        if settings.TELEGRAM_CHAT_ID and chat_id_str == str(settings.TELEGRAM_CHAT_ID):
            return True
        return False

    async def get_user_status(self, chat_id: int) -> tuple[bool, bool, Optional[UserModel]]:
        """Devuelve (is_admin, is_guardian, user_obj)."""
        chat_id_str = str(chat_id)
        if chat_id_str == str(self.admin_chat_id):
            return True, True, None

        def _fetch_user_sync() -> tuple[bool, bool, Optional[UserModel]]:
            from src.interfaces.api.deps import is_admin as is_admin_user

            with SessionCloud() as db:
                user = db.query(UserModel).filter(UserModel.telegram_chat_id == chat_id_str).first()
                if user:
                    _ = (user.id, user.username, user.email, user.role, user.telegram_chat_id, user.is_active)
                    is_admin_role = is_admin_user(user)
                    db.expunge(user)
                    return is_admin_role, True, user
            return False, False, None

        return await asyncio.to_thread(_fetch_user_sync)

    async def start_polling(self):
        """Inicia el bucle asíncrono de escucha en segundo plano."""
        if not self.enabled:
            return
            
        self.running = True
        logger.info("📡 Telegram Listener: Iniciando bucle de escucha en segundo plano...")
        telegram_service.log_telemetry("LISTENER_START", {"status": "running"})
        
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        
        # Limpiar actualizaciones previas al arrancar
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, params={"limit": 100}, timeout=10)
                if resp.status_code == 200:
                    results = resp.json().get("result", [])
                    if results:
                        self.offset = results[-1]["update_id"] + 1
        except Exception as e:
            logger.error(f"TelegramListener startup clean failed: {e}")

        while self.running:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        url, 
                        params={"offset": self.offset, "timeout": 20}, 
                        timeout=25
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("result", [])
                        for u in results:
                            self.offset = u["update_id"] + 1
                            if "callback_query" in u:
                                await self.process_callback_query(u["callback_query"])
                            elif "message" in u:
                                await self.process_message(u["message"])
                    elif resp.status_code == 409:
                        # Conflicto de webhook u otra instancia
                        logger.warning("TelegramListener Conflict (409). Esperando 10s...")
                        await asyncio.sleep(10)
            except httpx.RequestError as exc:
                # Silencioso ante pérdidas temporales de red
                pass
            except Exception as e:
                logger.error(f"Error en bucle de TelegramListener: {e}")
            await asyncio.sleep(2)

    def stop_polling(self):
        self.running = False
        logger.info("📡 Telegram Listener: Deteniendo bucle de escucha.")
        telegram_service.log_telemetry("LISTENER_STOP", {"status": "stopped"})

    async def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None):
        """Responde a un callback_query de Telegram para finalizar la animación de carga."""
        url = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            logger.debug(f"Error answering callback query: {e}")

    async def process_callback_query(self, callback_query: dict):
        """Procesa pulsaciones de botones Inline de Telegram."""
        cq_id = callback_query.get("id")
        from_user = callback_query.get("from", {})
        user_id = from_user.get("id")
        message = callback_query.get("message", {})
        chat = message.get("chat", {})
        chat_id = chat.get("id") or user_id
        data = callback_query.get("data", "")

        if not cq_id or not chat_id:
            return

        telegram_service.log_telemetry("CALLBACK_QUERY_RECEIVED", {
            "chat_id": chat_id,
            "username": from_user.get("username"),
            "data": data
        })

        is_admin, is_guardian, _ = await self.get_user_status(chat_id)
        if not is_admin:
            await self.answer_callback_query(cq_id, "❌ Acción solo para Administradores.")
            return

        if data == "ssl:renew":
            await self.answer_callback_query(cq_id, "⏳ Iniciando renovación de certificados SSL...")
            await telegram_service.send_message(
                "🔒 <b>[Oráculo SSL]</b> Renovación forzada solicitada desde Telegram. Ejecutando...",
                chat_id=chat_id
            )
            from src.application.services.ssl_service import SSLService
            asyncio.create_task(SSLService.renew_ssl_certificate(force=True))
        elif data == "alerts:toggle":
            def _toggle_alerts_sync() -> bool:
                from src.application.services.telegram_filter_service import (
                    is_telegram_only_missing_enabled,
                    set_telegram_only_missing_enabled,
                )
                with SessionCloud() as db:
                    new_val_inner = not is_telegram_only_missing_enabled(db)
                    set_telegram_only_missing_enabled(db, new_val_inner)
                    return new_val_inner

            new_val = await asyncio.to_thread(_toggle_alerts_sync)
            mode_text = "SOLO figuras que NO posees" if new_val else "TODAS las ofertas destacadas"
            await self.answer_callback_query(cq_id, f"✅ Modo cambiado: {mode_text}")
            await self.cmd_alertas(chat_id)
        elif data == "ssl:status":
            await self.answer_callback_query(cq_id, "🔍 Consultando estado SSL...")
            await self.cmd_ssl_status(chat_id)
        elif data.startswith("device:allow:"):
            if not self.is_sovereign_admin(chat_id):
                await self.answer_callback_query(cq_id, "❌ Acción restringida exclusivamente al Gran Arquitecto.")
                return
            dev_id = int(data.split(":")[2])
            def _allow_device_sync() -> tuple[Optional[str], Optional[str]]:
                with SessionCloud() as db:
                    device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == dev_id).first()
                    if not device:
                        return None, None
                    device.is_authorized = True
                    dev_id_str = str(device.device_id)
                    dev_name_val = str(device.device_name or dev_id_str)
                    db.commit()
                    from src.core.security import SecurityShield
                    SecurityShield.invalidate_device_cache(dev_id_str)
                    return dev_id_str, dev_name_val

            dev_id_str, dev_name = await asyncio.to_thread(_allow_device_sync)
            if not dev_id_str:
                await self.answer_callback_query(cq_id, "❌ Dispositivo no encontrado.")
                return
            await self.answer_callback_query(cq_id, f"✅ Dispositivo '{dev_name}' autorizado.")
            await telegram_service.send_message(
                f"🛡️ <b>[Escudo de Eternia]</b> Dispositivo <b>{html.escape(dev_name or '')}</b> (<code>{html.escape(dev_id_str)}</code>) ha sido <b>AUTORIZADO</b> con éxito.",
                chat_id=chat_id
            )
        elif data.startswith("device:deny:"):
            if not self.is_sovereign_admin(chat_id):
                await self.answer_callback_query(cq_id, "❌ Acción restringida exclusivamente al Gran Arquitecto.")
                return
            dev_id = int(data.split(":")[2])

            def _deny_device_sync() -> Optional[str]:
                with SessionCloud() as db:
                    device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == dev_id).first()
                    if not device:
                        return None
                    dev_id_str = str(device.device_id)
                    dev_name_val = str(device.device_name or dev_id_str)
                    db.delete(device)
                    db.commit()
                    from src.core.security import SecurityShield
                    SecurityShield.invalidate_device_cache(dev_id_str)
                    return dev_name_val

            dev_name = await asyncio.to_thread(_deny_device_sync)
            if dev_name is None:
                await self.answer_callback_query(cq_id, "❌ Dispositivo no encontrado.")
                return
            safe_dev_name = html.escape(dev_name)
            await self.answer_callback_query(cq_id, f"🚫 Dispositivo '{safe_dev_name}' bloqueado.")
            await telegram_service.send_message(
                f"🛑 <b>[Escudo de Eternia]</b> Dispositivo <b>{safe_dev_name}</b> ha sido <b>BLOQUEADO Y ELIMINADO</b>.",
                chat_id=chat_id
            )
        else:
            await self.answer_callback_query(cq_id)

    async def process_message(self, message: dict):
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "").strip()
        from_user = message.get("from", {})
        
        if not chat_id or not text:
            return
            
        telegram_service.log_telemetry("COMMAND_RECEIVED", {
            "chat_id": chat_id,
            "username": from_user.get("username"),
            "text": text
        })
        
        # Comprobar roles y permisos
        is_admin, is_guardian, user = await self.get_user_status(chat_id)
        
        # Detección inteligente de enlaces de Wallapop compartidos desde móvil/chat (sin comando)
        if "wallapop.com/item/" in text:
            if not is_guardian:
                await telegram_service.send_message("🔒 Debes estar registrado como Guardián (/register) para importar ofertas.", chat_id=chat_id)
                return
            await self.cmd_import_wallapop(chat_id, [text])
            return

        # Solo procesar comandos que inicien con '/'
        # --- Procesamiento en Lenguaje Natural (El Ojo del Oráculo) ---
        if not text.startswith("/"):
            if not is_guardian:
                msg = (
                    "<b>🔒 Acceso Restringido</b>\n\n"
                    "No estás registrado como Guardián del Oráculo. Por favor, asocia tu chat ID enviando:\n"
                    "<code>/register [tu_usuario_del_sistema]</code>"
                )
                await telegram_service.send_message(msg, chat_id=chat_id)
                return
            
            from src.application.services.telegram_oracle_ai import OracleAssistantAI
            if not user:
                await telegram_service.send_message("🔒 Usuario no vinculado correctamente.", chat_id=chat_id)
                return
            ai_reply = await OracleAssistantAI.process_user_query(text, user_id=user.id)
            await telegram_service.send_message(ai_reply, chat_id=chat_id)
            return
            
        parts = text.split(maxsplit=2)
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # --- Comando Público / Registro ---
        if command == "/register":
            await self.cmd_register(chat_id, args)
            return
            
        # Si no es un usuario registrado (ni admin ni guardián), denegar y pedir registro
        if not is_guardian:
            msg = (
                "<b>🔒 Acceso Restringido</b>\n\n"
                "No estás registrado como Guardián del Oráculo. Por favor, asocia tu chat ID enviando:\n"
                "<code>/register [tu_usuario_del_sistema]</code>"
            )
            await telegram_service.send_message(msg, chat_id=chat_id)
            return

        # --- Comandos Comunes (Administradores y Guardianes) ---
        if command == "/help":
            await self.cmd_help(chat_id, is_admin)
        elif command == "/purgatorio":
            await self.cmd_purgatorio(chat_id)
        elif command == "/buscar":
            query = " ".join(args) if args else ""
            await self.cmd_buscar(chat_id, query)
        elif command in ["/wallapop", "/import"]:
            await self.cmd_import_wallapop(chat_id, args)
        elif command in ["/caza", "/hunt"]:
            await self.cmd_caza(chat_id, args)
        elif command in ["/centinela", "/sentinel"]:
            await self.cmd_centinela(chat_id, args)
        elif command in ["/update_image", "/actualizar_imagen", "/af411_image"]:
            await self.cmd_update_image(chat_id, args)
        elif command in ["/alertas", "/notificaciones"]:
            await self.cmd_alertas(chat_id)
            
        # --- Comandos de Administrador Only ---
        elif is_admin:
            if command in ["/harvest_lore", "/lore"]:
                # Escribe en el canon global (character_lore) y raspa la wiki: solo administradores.
                await self.cmd_harvest_lore(chat_id, args)
            elif command == "/status":
                await self.cmd_status(chat_id)
            elif command in ["/ssl", "/ssl_status"]:
                await self.cmd_ssl_status(chat_id)
            elif command in ["/renew_ssl", "/renovar_ssl"]:
                await self.cmd_renew_ssl(chat_id)
            elif command in ["/tokens", "/cuotas", "/apify"]:
                await self.cmd_tokens(chat_id)
            elif command in ["/nexus", "/nexus_job"]:
                query_term = " ".join(args) if args else "auto"
                await self.cmd_nexus(chat_id, query_term)
            elif command in ["/devices", "/dispositivos"]:
                await self.cmd_devices(chat_id)
            elif command in ["/approve", "/aprobar"]:
                await self.cmd_approve_device(chat_id, args)
            elif command in ["/deny", "/rechazar"]:
                await self.cmd_deny_device(chat_id, args)
            elif command == "/run":
                scraper_name = args[0] if args else "all"
                query_term = args[1] if len(args) > 1 else None
                await self.cmd_run(chat_id, scraper_name, query_term)
            elif command == "/stop":
                await self.cmd_stop(chat_id)
            else:
                await telegram_service.send_message("❌ Comando administrativo no reconocido. Escribe /help.", chat_id=chat_id)
        else:
            await telegram_service.send_message("❌ No tienes permisos de administrador para ejecutar este comando.", chat_id=chat_id)

    async def cmd_register(self, chat_id: int, args: list):
        if not args:
            await telegram_service.send_message("❌ Uso: <code>/register [nombre_usuario] [clave_vinculacion]</code>", chat_id=chat_id)
            return

        from src.core.security import SecurityShield

        is_master_chat = bool(settings.TELEGRAM_CHAT_ID) and str(chat_id) == str(settings.TELEGRAM_CHAT_ID)
        provided_token = args[1].strip() if len(args) > 1 else ""
        if not is_master_chat and not (provided_token and SecurityShield.safe_compare_digest(provided_token, settings.ORACULO_API_KEY)):
            await telegram_service.send_message("🔒 Se requiere clave de autorización del Arquitecto para vincular un chat externo.", chat_id=chat_id)
            return

        username = args[0].strip()
        chat_id_str = str(chat_id)

        def _register_chat_sync() -> tuple[str, Optional[str]]:
            with SessionCloud() as db:
                db_user = db.query(UserModel).filter(UserModel.username == username).first()
                if not db_user:
                    return "not_found", None
                if db_user.telegram_chat_id and db_user.telegram_chat_id != chat_id_str:
                    return "conflict", None
                linked_name = str(db_user.username)
                db_user.telegram_chat_id = chat_id_str
                db.commit()
                return "ok", linked_name

        status_code, linked_username = await asyncio.to_thread(_register_chat_sync)
        if status_code == "not_found":
            await telegram_service.send_message(f"❌ Usuario <b>{html.escape(username)}</b> no encontrado en el sistema.", chat_id=chat_id)
            return
        if status_code == "conflict":
            await telegram_service.send_message("❌ Este usuario ya tiene otro chat ID asociado.", chat_id=chat_id)
            return

        msg = (
            f"<b>✅ Registro Exitoso</b>\n\n"
            f"Bienvenido, Guardián <b>{html.escape(linked_username or username)}</b>. Tu chat ID ha sido vinculado.\n"
            f"A partir de ahora recibirás alertas de tu lista de deseos y tus alertas de precios configuradas."
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_help(self, chat_id: int, is_admin: bool):
        lines = ["<b>📖 Comandos del Oráculo de Eternia</b>\n"]
        lines.append("<b>Comunes:</b>")
        lines.append("• <code>/purgatorio</code> - Muestra ofertas pendientes de clasificar.")
        lines.append("• <code>/buscar [figura]</code> - Busca ofertas activas en la base de datos.")
        lines.append("• <code>/wallapop [enlace]</code> - Importa un artículo de Wallapop al Purgatorio (o comparte el link directo).")
        lines.append("• <code>/caza</code> - Incursión instantánea en Vinted (4 consultas canónicas) con alerta push de gangas bajo precio medio.")
        lines.append("• <code>/caza [figura]</code> - Caza personalizada de una figura en Vinted.")
        lines.append("• <code>/centinela</code> - Consulta el estado del Centinela Autónomo 24/7 de Vinted.")
        lines.append("• <code>/centinela [on|off]</code> - Activa o pausa las incursiones automáticas (100-120 min).")
        lines.append("• <code>/alertas</code> - Configurar filtro de alertas push (solo figuras que no poseo).")
        lines.append("• <code>/help</code> - Muestra este menú de ayuda.")
        
        if is_admin:
            lines.append("\n<b>Administrador / Soberano Only:</b>")
            lines.append("• <code>/status</code> - Consulta de salud del sistema, scrapers y base de datos.")
            lines.append("• <code>/ssl</code> - Diagnóstico en vivo y telemetría de certificados SSL.")
            lines.append("• <code>/renew_ssl</code> - Forzar renovación inmediata de certificados SSL.")
            lines.append("• <code>/tokens</code> - Comprobación en vivo de Apify y ScraperAPI (0 créditos).")
            lines.append("• <code>/nexus</code> - Incursión rápida de novedades (Wallapop + Smyths Toys).")
            lines.append("• <code>/nexus completo</code> - Incursión profunda (5 familias Wallapop + Smyths Toys).")
            lines.append("• <code>/nexus [consulta]</code> - Búsqueda personalizada en Wallapop y Smyths Toys.")
            lines.append("• <code>/devices</code> - Listar y gestionar dispositivos con botones de aprobación.")
            lines.append("• <code>/approve [id]</code> - Autorizar acceso a un dispositivo.")
            lines.append("• <code>/deny [id]</code> - Bloquear/eliminar un dispositivo.")
            lines.append("• <code>/run [tienda] [búsqueda]</code> - Lanza un recolector en segundo plano (ej: <code>/run wallapop heman</code>).")
            lines.append("• <code>/stop</code> - Protocolo de parada de emergencia para detener scrapers.")
            
        await telegram_service.send_message("\n".join(lines), chat_id=chat_id)

    async def cmd_alertas(self, chat_id: int):
        def _read_alert_filter_sync() -> bool:
            from src.application.services.telegram_filter_service import is_telegram_only_missing_enabled
            with SessionCloud() as db:
                return is_telegram_only_missing_enabled(db)

        only_missing = await asyncio.to_thread(_read_alert_filter_sync)

        status_badge = "🟢 <b>ACTIVADO (Recomendado)</b>" if only_missing else "⚪ <b>DESACTIVADO</b>"
        explanation = (
            "Solo recibirás notificaciones push de ofertas y gangas para figuras que <b>NO tengas ya aseguradas</b> en tu Fortaleza."
            if only_missing else
            "Recibirás notificaciones push de <b>TODAS las ofertas y gangas destacadas</b>, incluso si ya posees la figura en tu colección."
        )

        msg = (
            "🔔 <b>[Filtro de Notificaciones Push de Telegram]</b>\n\n"
            f"• <b>Estado:</b> {status_badge}\n\n"
            f"📝 <i>{explanation}</i>\n\n"
            "Puedes alternar este ajuste pulsando el botón a continuación o desde la Web en <b>Ajustes del Sistema</b>."
        )

        btn_text = "⚪ Cambiar a: Notificar TODO" if only_missing else "🟢 Cambiar a: Solo NO Poseídos"
        keyboard = {
            "inline_keyboard": [
                [{"text": btn_text, "callback_data": "alerts:toggle"}]
            ]
        }
        await telegram_service.send_message(msg, chat_id=chat_id, reply_markup=keyboard)

    async def cmd_purgatorio(self, chat_id: int):
        def _read_purgatory_stats_sync() -> tuple[int, int, int, int]:
            with SessionCloud() as db:
                return (
                    db.query(PendingMatchModel).count(),
                    db.query(PendingMatchModel).filter(PendingMatchModel.is_vintage == True).count(),
                    db.query(PendingMatchModel).filter(PendingMatchModel.is_vintage == False).count(),
                    db.query(PendingMatchModel).filter(PendingMatchModel.opportunity_score >= 80).count(),
                )

        total, vintage, modern, high_opp = await asyncio.to_thread(_read_purgatory_stats_sync)
            
        msg = (
            f"<b>🗳️ Estado del Purgatorio del Oráculo</b>\n\n"
            f"📦 <b>Total Ofertas Pendientes:</b> {total}\n"
            f"🏺 <b>Lotes/Muñecos Vintage:</b> {vintage}\n"
            f"🛡️ <b>Artículos Modernos:</b> {modern}\n"
            f"🔥 <b>Oportunidades Puntuadas (80+):</b> {high_opp}"
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_buscar(self, chat_id: int, query: str):
        if not query:
            await telegram_service.send_message("❌ Uso: <code>/buscar [nombre_figura]</code>", chat_id=chat_id)
            return

        from sqlalchemy.orm import joinedload

        safe_query = html.escape(query)

        def _search_offers_sync() -> list[str]:
            result_lines: list[str] = []
            with SessionCloud() as db:
                search_query = f"%{query}%"
                offers = (
                    db.query(OfferModel)
                    .options(joinedload(OfferModel.product))
                    .join(ProductModel)
                    .filter(
                        OfferModel.is_available == True,
                        ProductModel.name.like(search_query),
                    )
                    .order_by(OfferModel.price)
                    .limit(5)
                    .all()
                )
                if offers:
                    result_lines.append(f"<b>🔍 Top 5 Ofertas más baratas para '{safe_query}':</b>\n")
                    for o in offers:
                        prod_name = html.escape(o.product.name) if o.product and o.product.name else "Desconocido"
                        shop = html.escape(o.shop_name or "Tienda")
                        url = html.escape(o.url or "", quote=True)
                        result_lines.append(
                            f"• <b>{prod_name}</b>\n"
                            f"  💰 {o.price:.2f}€ | 🏪 {shop}\n"
                            f"  🔗 <a href='{url}'>Ver Oferta en Web</a>\n"
                        )
            return result_lines

        lines = await asyncio.to_thread(_search_offers_sync)

        if not lines:
            await telegram_service.send_message(f"🔍 No se encontraron ofertas activas para <b>'{safe_query}'</b>.", chat_id=chat_id)
            return

        await telegram_service.send_message("\n".join(lines), chat_id=chat_id)

    async def cmd_status(self, chat_id: int):
        def _fetch_status_sync() -> tuple[list[tuple[str, str]], int, int]:
            with SessionCloud() as db:
                statuses = db.query(ScraperStatusModel).all()
                status_rows = [(str(s.spider_name or ""), str(s.status or "")) for s in statuses]
                total_products_val = db.query(ProductModel).count()
                total_offers_val = db.query(OfferModel).filter(OfferModel.is_available == True).count()
                return status_rows, total_products_val, total_offers_val

        status_rows, total_products, total_offers = await asyncio.to_thread(_fetch_status_sync)

        scraper_lines = []
        for spider_name, status_val in status_rows:
            icon = "🟢" if status_val == "completed" else "🔴" if "error" in status_val else "⏳" if status_val == "running" else "⚪"
            scraper_lines.append(f"{icon} <b>{html.escape(spider_name)}:</b> {html.escape(status_val.upper())}")
            
        msg = (
            f"<b>📊 Estado del Sistema</b>\n\n"
            f"📚 <b>Catálogo de Productos:</b> {total_products}\n"
            f"🏷️ <b>Ofertas Activas Disponibles:</b> {total_offers}\n\n"
            f"🤖 <b>Estado de Recolectores:</b>\n" + "\n".join(scraper_lines)
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_run(self, chat_id: int, scraper_name: str, query: Optional[str]):
        # Validar tienda
        valid_spiders = ["fantasia", "frikiverso", "frikimaz", "electropolis", "pixelatoy", "amazon", "detoyboys", "ebay", "vinted", "wallapop", "toymieu", "time4actiontoysde", "bigbadtoystore", "smythstoys", "dvdstorespain", "triguetech", "bixoto", "all"]
        safe_scraper = html.escape(scraper_name)

        if scraper_name.lower() not in valid_spiders:
            await telegram_service.send_message(f"❌ Tienda <b>'{safe_scraper}'</b> no válida.\nOpciones: {', '.join(valid_spiders)}", chat_id=chat_id)
            return

        if query:
            from src.core.vintage_utils import check_is_vintage
            if check_is_vintage(query):
                await telegram_service.send_message(
                    f"⛔ Búsqueda bloqueada por política del Oráculo: los términos vintage/años 80 están deshabilitados temporalmente (<b>{html.escape(query)}</b>).",
                    chat_id=chat_id
                )
                return

        # Ejecutar en thread/ejecutor de asyncio sin bloquear el event loop
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, run_scraper_task, scraper_name, "telegram", query)

        safe_query = html.escape(query) if query else "auto"
        await telegram_service.send_message(
            f"🚀 <b>Incursión Iniciada</b>\n\n"
            f"Scraper <b>{safe_scraper}</b> ejecutándose en segundo plano para <b>'{safe_query}'</b>.\n"
            f"Te avisaré si detectamos compras obligatorias o alertas de wishlist.",
            chat_id=chat_id
        )

    async def cmd_stop(self, chat_id: int):
        try:
            # Ejecutar parada en thread separado para no bloquear el event loop
            res = await asyncio.to_thread(stop_scrapers)
            killed = res.get("killed_processes", 0)
            await telegram_service.send_message(
                f"🛑 <b>Parada de Emergencia Completada</b>\n\n"
                f"Se han eliminado <b>{killed}</b> procesos de scrapers activos y purificado los estados en base de datos.",
                chat_id=chat_id
            )
        except Exception as e:
            await telegram_service.send_message(f"❌ Error al detener los scrapers: {html.escape(str(e))}", chat_id=chat_id)

    async def cmd_ssl_status(self, chat_id: int):
        from src.application.services.ssl_service import SSLService
        status = await asyncio.to_thread(SSLService.get_certificate_status)

        icon = "🟢" if status.get("status") == "ACTIVE" else "🟡" if status.get("status") == "EXPIRING_SOON" else "🔴"
        valid_from = status.get("valid_from")
        valid_until = status.get("valid_until")
        next_renewal = status.get("next_renewal_recommended")

        from_str = html.escape(valid_from.strftime("%d/%m/%Y %H:%M UTC")) if valid_from else "N/D"
        until_str = html.escape(valid_until.strftime("%d/%m/%Y %H:%M UTC")) if valid_until else "N/D"
        next_str = html.escape(next_renewal.strftime("%d/%m/%Y")) if next_renewal else "N/D"

        msg = (
            f"🔒 <b>[Oráculo SSL] Diagnóstico de Certificados</b>\n\n"
            f"• Dominio: <code>{html.escape(str(status.get('domain') or ''))}</code>\n"
            f"• Estado: {icon} <b>{html.escape(str(status.get('status') or ''))}</b> ({status.get('days_remaining')} días restantes)\n"
            f"• Emisor: <b>{html.escape(str(status.get('issuer') or ''))}</b>\n"
            f"• Emisión: <code>{from_str}</code>\n"
            f"• Caducidad: <code>{until_str}</code>\n"
            f"• Próxima Renovación Recomendada: <b>{next_str}</b>\n\n"
            f"ℹ️ <i>{html.escape(str(status.get('details') or ''))}</i>"
        )
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Forzar Renovación SSL", "callback_data": "ssl:renew"},
                    {"text": "📊 Actualizar Estado", "callback_data": "ssl:status"}
                ]
            ]
        }
        await telegram_service.send_message(msg, chat_id=chat_id, reply_markup=keyboard)

    async def cmd_renew_ssl(self, chat_id: int):
        await telegram_service.send_message(
            "🔒 <b>[Oráculo SSL]</b> Iniciando renovación forzada de certificados SSL en segundo plano...",
            chat_id=chat_id
        )
        from src.application.services.ssl_service import SSLService
        asyncio.create_task(SSLService.renew_ssl_certificate(force=True))

    async def cmd_devices(self, chat_id: int):
        if not self.is_sovereign_admin(chat_id):
            await telegram_service.send_message("❌ Comando restringido exclusivamente al Gran Arquitecto.", chat_id=chat_id)
            return

        def _list_devices_sync() -> list[tuple[int, str, str, bool]]:
            with SessionCloud() as db:
                devices_db = db.query(AuthorizedDeviceModel).order_by(AuthorizedDeviceModel.id.desc()).limit(15).all()
                return [
                    (int(d.id), str(d.device_id or ""), str(d.device_name or "Sin Nombre"), bool(d.is_authorized))
                    for d in devices_db
                ]

        devices = await asyncio.to_thread(_list_devices_sync)

        if not devices:
            await telegram_service.send_message("🛡️ <b>[Escudo de Eternia]</b> No hay dispositivos registrados en la base de datos.", chat_id=chat_id)
            return

        lines = ["🛡️ <b>[Escudo de Eternia] Dispositivos Registrados:</b>\n"]
        buttons = []

        for dev_pk, device_id_str, raw_name, is_auth in devices:
            status_icon = "🟢" if is_auth else "🔴"
            status_text = "AUTORIZADO" if is_auth else "BLOQUEADO"
            safe_name = html.escape(raw_name)
            safe_short_id = html.escape(device_id_str[:16])
            lines.append(f"{status_icon} <b>#{dev_pk} {safe_name}</b> - {status_text}\n  🆔 <code>{safe_short_id}...</code>")

            if not is_auth:
                buttons.append([
                    {"text": f"✅ Aprobar #{dev_pk} ({raw_name[:12]})", "callback_data": f"device:allow:{dev_pk}"},
                    {"text": f"🗑️ Eliminar #{dev_pk}", "callback_data": f"device:deny:{dev_pk}"}
                ])
            else:
                buttons.append([
                    {"text": f"🚫 Revocar/Eliminar #{dev_pk} ({raw_name[:12]})", "callback_data": f"device:deny:{dev_pk}"}
                ])

        keyboard = {"inline_keyboard": buttons} if buttons else None
        await telegram_service.send_message("\n".join(lines), chat_id=chat_id, reply_markup=keyboard)

    async def cmd_approve_device(self, chat_id: int, args: list):
        if not self.is_sovereign_admin(chat_id):
            await telegram_service.send_message("❌ Comando restringido exclusivamente al Gran Arquitecto.", chat_id=chat_id)
            return
        if not args:
            await telegram_service.send_message("❌ Uso: <code>/aprobar [ID_o_Fingerprint]</code>", chat_id=chat_id)
            return
        
        target = args[0].strip()

        def _approve_device_sync() -> tuple[Optional[str], Optional[str]]:
            with SessionCloud() as db:
                device = None
                if target.isdigit():
                    device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == int(target)).first()
                if not device:
                    device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id.like(f"%{target}%")).first()

                if not device:
                    return None, None

                device.is_authorized = True
                dev_id_val = str(device.device_id)
                dev_name_val = str(device.device_name or dev_id_val)
                db.commit()
                from src.core.security import SecurityShield
                SecurityShield.invalidate_device_cache(dev_id_val)
                return dev_id_val, dev_name_val

        dev_id_str, raw_dev_name = await asyncio.to_thread(_approve_device_sync)
        if not dev_id_str:
            await telegram_service.send_message(f"❌ No se encontró ningún dispositivo para '<b>{html.escape(target)}</b>'.", chat_id=chat_id)
            return

        dev_name = html.escape(raw_dev_name or dev_id_str)

        await telegram_service.send_message(
            f"✅ <b>[Escudo de Eternia]</b> Dispositivo <b>{dev_name}</b> (<code>{html.escape(dev_id_str)}</code>) ha sido <b>AUTORIZADO</b> permanentemente.",
            chat_id=chat_id
        )

    async def cmd_deny_device(self, chat_id: int, args: list):
        if not self.is_sovereign_admin(chat_id):
            await telegram_service.send_message("❌ Comando restringido exclusivamente al Gran Arquitecto.", chat_id=chat_id)
            return
        if not args:
            await telegram_service.send_message("❌ Uso: <code>/rechazar [ID_o_Fingerprint]</code>", chat_id=chat_id)
            return
        
        target = args[0].strip()

        def _deny_device_cmd_sync() -> Optional[str]:
            with SessionCloud() as db:
                device = None
                if target.isdigit():
                    device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == int(target)).first()
                if not device:
                    device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id.like(f"%{target}%")).first()

                if not device:
                    return None

                dev_id_str = str(device.device_id)
                dev_name_val = str(device.device_name or dev_id_str)
                db.delete(device)
                db.commit()
                from src.core.security import SecurityShield
                SecurityShield.invalidate_device_cache(dev_id_str)
                return dev_name_val

        raw_dev_name = await asyncio.to_thread(_deny_device_cmd_sync)
        if raw_dev_name is None:
            await telegram_service.send_message(f"❌ No se encontró ningún dispositivo para '<b>{html.escape(target)}</b>'.", chat_id=chat_id)
            return

        dev_name = html.escape(raw_dev_name)

        await telegram_service.send_message(
            f"🛑 <b>[Escudo de Eternia]</b> Dispositivo <b>{dev_name}</b> ha sido <b>BLOQUEADO Y ELIMINADO</b>.",
            chat_id=chat_id
        )

    async def cmd_import_wallapop(self, chat_id: int, args: list):
        if not args:
            await telegram_service.send_message("❌ Uso: <code>/wallapop [enlace_de_wallapop]</code>", chat_id=chat_id)
            return

        raw_text = " ".join(args).strip()
        from src.core.url_utils import normalize_url
        from src.application.services.wallapop_bridge import WallapopBridge
        from src.core.vintage_utils import validate_motu_relevance

        # Extraer URL del texto compartido (por ejemplo si viene de "Compartir en Telegram")
        url_match = re.search(r"https?://[^\s]*wallapop\.com/item/[^\s]+", raw_text)
        if not url_match:
            await telegram_service.send_message("❌ No se encontró un enlace válido de producto de Wallapop (debe contener <code>/item/</code>).", chat_id=chat_id)
            return
            
        url = normalize_url(url_match.group(0))
        await telegram_service.send_message("🔍 <i>Extrayendo detalles del producto en Wallapop...</i>", chat_id=chat_id)

        try:
            details = await WallapopBridge.get_item_details(url)
            if not details or not details.get("title"):
                await telegram_service.send_message("❌ No se pudieron obtener los datos de la ficha de Wallapop en este momento.", chat_id=chat_id)
                return

            title = details.get("title", "")
            price = details.get("price", 0.0)
            images = details.get("images", [])
            image_url = images[0] if images else None

            from src.core.vintage_utils import check_is_vintage
            if check_is_vintage(title):
                await telegram_service.send_message(
                    f"⛔ <b>Artículo vintage rechazado:</b> <b>{html.escape(title)}</b> (búsquedas vintage deshabilitadas temporalmente).",
                    chat_id=chat_id
                )
                return

            # Relevancia MOTU
            is_relevant, reason = validate_motu_relevance(title)
            if not is_relevant:
                await telegram_service.send_message(
                    f"⚠️ <b>Artículo descartado por filtro MOTU:</b>\n"
                    f"• <b>Título:</b> {html.escape(title)}\n"
                    f"• <i>Motivo: {html.escape(str(reason))}</i>",
                    chat_id=chat_id
                )
                return

            parsed_price = float(price) if price else 0.0

            def _import_wallapop_sync() -> bool:
                with SessionCloud() as db:
                    existing_p = db.query(PendingMatchModel).filter(PendingMatchModel.url == url).first()
                    existing_o = db.query(OfferModel).filter(OfferModel.url == url).first()
                    if existing_p or existing_o:
                        return False
                    new_pending = PendingMatchModel(
                        scraped_name=title,
                        price=parsed_price,
                        url=url,
                        shop_name="Wallapop",
                        image_url=image_url,
                        source_type="Peer-to-Peer",
                        sale_type="Fixed_P2P"
                    )
                    db.add(new_pending)
                    db.commit()
                    return True

            created = await asyncio.to_thread(_import_wallapop_sync)
            safe_title = html.escape(title)
            safe_price = html.escape(str(price))
            safe_url = html.escape(url or "", quote=True)

            if not created:
                await telegram_service.send_message(
                    f"ℹ️ El artículo <b>{safe_title}</b> ({safe_price} €) ya existe en la base de datos del Oráculo.",
                    chat_id=chat_id
                )
                return

            msg = (
                f"🎁 <b>[Wallapop: Importación Exitosa]</b>\n\n"
                f"• <b>Artículo:</b> {safe_title}\n"
                f"• <b>Precio:</b> <b>{safe_price} €</b>\n"
                f"• <b>Enlace:</b> <a href=\"{safe_url}\">Ver en Wallapop</a>\n\n"
                f"✅ <i>Añadido al Purgatorio del Oráculo para revisión y matching.</i>"
            )
            await telegram_service.send_message(msg, chat_id=chat_id)

        except Exception as e:
            logger.error(f"Error al importar producto de Wallapop desde Telegram: {e}")
            await telegram_service.send_message(f"❌ Error al procesar el enlace: {html.escape(str(e))}", chat_id=chat_id)

    async def cmd_tokens(self, chat_id: int):
        await telegram_service.send_message("🔍 <i>Verificando estado de tokens de scraping (0 créditos consumidos)...</i>", chat_id=chat_id)
        
        t1 = settings.APIFY_TOKEN or os.environ.get("APIFY_TOKEN")
        t2 = settings.APIFY_TOKEN2 or getattr(settings, "APYFY_TOKEN2", None) or os.environ.get("APIFY_TOKEN2") or os.environ.get("APYFY_TOKEN2")
        t3 = settings.APIFY_TOKEN3 or os.environ.get("APIFY_TOKEN3")
        s_key = settings.SCRAPERAPI_KEY or os.environ.get("SCRAPERAPI_KEY")
        
        lines = ["🛡️ <b>[Oráculo: Diagnóstico de Tokens de Scraping]</b>\n<i>(Comprobación gratuita de metadatos: 0 créditos)</i>\n"]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Apify Tokens
            apify_list = [
                ("APIFY_TOKEN (Cuenta 1)", t1),
                ("APIFY_TOKEN2 (Cuenta 2)", t2),
                ("APIFY_TOKEN3 (Cuenta 3)", t3)
            ]
            
            for label, token in apify_list:
                if not token:
                    lines.append(f"🟡 <b>{label}:</b> No configurado en .env")
                    continue
                try:
                    res = await client.get(f"https://api.apify.com/v2/users/me?token={token.strip()}")
                    if res.status_code == 200:
                        data = res.json().get("data", {})
                        uname = data.get("username", "Desconocido")
                        plan = data.get("plan", {}).get("name", "Free")
                        lines.append(f"🟢 <b>{label}:</b> Operativo\n   👤 Usuario: <code>{uname}</code> | Plan: <b>{plan}</b>")
                    elif res.status_code in [401, 403]:
                        lines.append(f"🔴 <b>{label}:</b> Token INVÁLIDO o expirado (HTTP {res.status_code})")
                    else:
                        lines.append(f"🔴 <b>{label}:</b> Error HTTP {res.status_code}")
                except Exception as e:
                    lines.append(f"⚠️ <b>{label}:</b> Error de red ({e})")
                    
            # 2. ScraperAPI Key
            if not s_key:
                lines.append("\n🟡 <b>SCRAPERAPI_KEY:</b> No configurada en .env")
            else:
                try:
                    res = await client.get(f"https://api.scraperapi.com/account?api_key={s_key.strip()}")
                    if res.status_code == 200:
                        data = res.json()
                        req_count = data.get("requestCount", 0)
                        req_limit = data.get("requestLimit", 0)
                        concurrency = data.get("concurrencyLimit", 0)
                        lines.append(f"\n🟢 <b>SCRAPERAPI_KEY:</b> Operativa\n   📊 Consumo: <b>{req_count} / {req_limit}</b> peticiones (Concurrencia: {concurrency})")
                    elif res.status_code in [401, 403]:
                        lines.append(f"\n🔴 <b>SCRAPERAPI_KEY:</b> Clave INVÁLIDA o suspendida (HTTP {res.status_code})")
                    else:
                        lines.append(f"\n🔴 <b>SCRAPERAPI_KEY:</b> Error HTTP {res.status_code}")
                except Exception as e:
                    lines.append(f"\n⚠️ <b>SCRAPERAPI_KEY:</b> Error de red ({e})")

        await telegram_service.send_message("\n".join(lines), chat_id=chat_id)

    async def cmd_nexus(self, chat_id: int, query_term: str):
        from src.core.vintage_utils import check_is_vintage
        from src.domain.models import WallapopJobModel
        q_clean = query_term.strip().lower()
        if q_clean not in ["completo", "full", "deep", "exhaustivo", "auto", "basico", "basic", ""] and check_is_vintage(query_term):
            await telegram_service.send_message(
                f"⛔ Búsqueda bloqueada por política del Oráculo: los términos vintage/años 80 están deshabilitados temporalmente (<b>{html.escape(query_term)}</b>).",
                chat_id=chat_id
            )
            return
        if q_clean in ["completo", "full", "deep", "exhaustivo"]:
            job_desc = "🌟 <b>Incursión Profunda Escalonada</b> (5 Familias MOTU Origins en Wallapop & Smyths Toys)"
            target_query = "completo"
            cadence_note = "⏳ <i>Duración estimada: ~2.0 - 3.5 min (Pausas orgánicas entre consultas para evadir bloqueos).</i>"
        elif q_clean in ["auto", "basico", "basic", ""]:
            job_desc = "⚡ <b>Incursión Rápida de Novedades</b> (Wallapop + Smyths Toys: ~150 ofertas)"
            target_query = "auto"
            cadence_note = "⚡ <i>Duración estimada: ~10 - 25 seg.</i>"
        else:
            job_desc = f"🎯 <b>Búsqueda Personalizada:</b> '<code>{html.escape(query_term)}</code>' (Wallapop + Smyths Toys)"
            target_query = query_term
            cadence_note = "⚡ <i>Duración estimada: ~5 - 15 seg.</i>"

        def _create_nexus_job_sync() -> int:
            with SessionCloud() as db:
                job = WallapopJobModel(query=target_query, status="pending")
                db.add(job)
                db.commit()
                db.refresh(job)
                return job.id

        job_id = await asyncio.to_thread(_create_nexus_job_sync)

        msg = (
            f"⚡ <b>[Nexus Local Bridge]</b> Trabajo <b>#{job_id}</b> encolado.\n\n"
            f"• <b>Modo:</b> {job_desc}\n"
            f"• <b>Destino:</b> El Purgatorio del Oráculo\n"
            f"• {cadence_note}\n\n"
            f"🖥️ <i>Tu PC de casa (con opción [3] de <code>oraculo.ps1</code>) lo procesará con tu IP residencial limpia.</i>"
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_caza(self, chat_id: int, args: list):
        from src.application.services.vinted_hunter_service import VintedHunterService
        from src.core.vintage_utils import check_is_vintage
        query_term = " ".join(args).strip() if args else "auto"

        if query_term.lower() not in ["auto", "origins", "motu", ""] and check_is_vintage(query_term):
            await telegram_service.send_message(
                f"⛔ Caza bloqueada por política del Oráculo: los términos vintage/años 80 están deshabilitados temporalmente (<b>{html.escape(query_term)}</b>).",
                chat_id=chat_id
            )
            return

        if query_term.lower() in ["auto", "origins", "motu", ""]:
            desc = "Cuarteto Canónico MOTU (<i>motu origins, masters del universo, masters of the universe, he-man origins</i>)"
            actual_query = "auto"
        else:
            desc = f"Búsqueda Personalizada: '<code>{html.escape(query_term)}</code>'"
            actual_query = query_term
            
        await telegram_service.send_message(
            f"🏹 <b>[Cazador de Vinted: Incursión Activa]</b>\n\n"
            f"• <b>Modo:</b> {desc}\n"
            f"• <b>Objetivo:</b> Detectar ofertas bajo el precio medio de mercado (P25)\n"
            f"• <b>Destino:</b> Purgatorio + Alerta Inmediata si hay gangas\n\n"
            f"⏳ <i>Rastreando en la nube con huella Chrome segura...</i>",
            chat_id=chat_id
        )
        
        async def _run_hunter_bg():
            try:
                res = await VintedHunterService.run_hunt(query=actual_query, chat_id=str(chat_id))
                scraped = res.get("total_scraped", 0)
                bargains = res.get("bargains_found", 0)
                
                summary = (
                    f"🏁 <b>[Caza de Vinted: Finalizada con Éxito]</b>\n\n"
                    f"• 📦 <b>Ofertas Extraídas:</b> {scraped}\n"
                    f"• 🔥 <b>Gangas Bajo Precio Medio:</b> {bargains}\n\n"
                    f"✅ <i>Todas las ofertas válidas han sido inyectadas al Purgatorio del Oráculo.</i>"
                )
                await telegram_service.send_message(summary, chat_id=chat_id)
            except Exception as ex:
                logger.error(f"Error en ejecución de VintedHunter: {ex}")
                await telegram_service.send_message(f"⚠️ Error durante la caza de Vinted: {ex}", chat_id=chat_id)
                
        asyncio.create_task(_run_hunter_bg())

    async def cmd_centinela(self, chat_id: int, args: list):
        from src.application.services.vinted_sentinel_service import vinted_sentinel
        
        action = args[0].lower().strip() if args else "status"
        
        if action in ["on", "activar", "start"]:
            vinted_sentinel.start()
            status = vinted_sentinel.get_status()
            mins = status.get("next_run_in_minutes", 60)
            msg = (
                "🟢 <b>[Centinela de Vinted Activado]</b>\n\n"
                "• <b>Estado:</b> ⚡ Vigilancia 24/7 en marcha\n"
                "• <b>Cadencia:</b> Incursiones pseudoaleatorias cada 50 - 75 min\n"
                f"• <b>Próxima Incursión:</b> En ~{mins} minutos\n"
                "• <b>Destino:</b> Purgatorio + Alerta inmediata si hay gangas bajo P25\n\n"
                "🛡️ <i>Tu servidor velará día y noche sin requerir tu PC encendido.</i>"
            )
            await telegram_service.send_message(msg, chat_id=chat_id)
            return
            
        elif action in ["off", "pausar", "stop"]:
            vinted_sentinel.stop()
            msg = (
                "🔴 <b>[Centinela de Vinted Pausado]</b>\n\n"
                "• <b>Estado:</b> En reposo\n"
                "• Las incursiones automáticas han quedado detenidas.\n"
                "• Puedes reactivarlo en cualquier momento enviando <code>/centinela on</code>."
            )
            await telegram_service.send_message(msg, chat_id=chat_id)
            return

        # Estado general
        status = vinted_sentinel.get_status()
        is_active = status.get("is_running", False)
        state_badge = "🟢 <b>ACTIVO (24/7)</b>" if is_active else "🔴 <b>EN REPOSO</b>"
        mins_remaining = status.get("next_run_in_minutes", 0)
        total_hunts = status.get("total_hunts", 0)
        total_bargains = status.get("total_bargains", 0)
        using_az = "☁️ Microsoft Azure (GitHub Actions)" if status.get("using_github_dispatch") else "🖥️ Motor Asíncrono Local"

        msg = (
            f"🏹 <b>[Panel de Control: Centinela de Vinted]</b>\n\n"
            f"• <b>Estado:</b> {state_badge}\n"
            f"• <b>Infraestructura:</b> {using_az}\n"
            f"• <b>Cadencia:</b> 100 - 120 minutos aleatorios\n"
            f"• <b>Próxima Incursión:</b> {'En ~' + str(mins_remaining) + ' min' if is_active else 'N/A'}\n"
            f"• <b>Incursiones Realizadas:</b> {total_hunts}\n"
            f"• <b>Chollos Detectados:</b> {total_bargains}\n\n"
            f"<b>Comandos:</b>\n"
            f"• <code>/centinela on</code> - Activar vigilancia continua\n"
            f"• <code>/centinela off</code> - Pausar centinela\n"
            f"• <code>/caza</code> - Forzar incursión inmediata"
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_update_image(self, chat_id: int, args: list):
        """Descarga la imagen actualizada de una figura desde ActionFigure411."""
        if not args:
            await telegram_service.send_message("❌ Uso: <code>/update_image [ID_figura_o_producto]</code> (ej. <code>/update_image 14038</code>)", chat_id=chat_id)
            return

        target_id = args[0].strip()
        await telegram_service.send_message(f"🔄 Conectando con ActionFigure411 para actualizar la imagen de la figura <b>{html.escape(target_id)}</b>...", chat_id=chat_id)

        from src.application.services.catalog_refresh_service import CatalogRefreshService

        def _refresh_sync() -> dict:
            with SessionCloud() as db:
                return CatalogRefreshService.refresh_figure_image(db, target_id)

        result = await asyncio.to_thread(_refresh_sync)
        if result.get("success"):
            msg = (
                f"✅ <b>[Imagen Actualizada con Éxito]</b>\n\n"
                f"• <b>Figura:</b> {html.escape(str(result.get('name') or ''))}\n"
                f"• <b>ID Figura:</b> <code>{html.escape(str(result.get('figure_id') or ''))}</code>\n"
                f"• <b>ID Catálogo:</b> #{result.get('product_id')}\n"
                f"• <b>Nueva URL:</b> {html.escape(str(result.get('new_image_url') or ''))}"
            )
            await telegram_service.send_message(msg, chat_id=chat_id)
        else:
            err = html.escape(str(result.get("error", "Error desconocido")))
            await telegram_service.send_message(f"❌ No se pudo actualizar la imagen: {err}", chat_id=chat_id)

    async def cmd_harvest_lore(self, chat_id: int, args: list):
        """Cosecha lore desde Wiki Fandom para una figura o personaje (solo administradores)."""
        if not args:
            await telegram_service.send_message("❌ Uso: <code>/lore [nombre_personaje_o_id]</code> (ej. <code>/lore He-Man</code> o <code>/lore 1460</code>)", chat_id=chat_id)
            return

        query_str = " ".join(args).strip()
        if not query_str or len(query_str) > 120:
            await telegram_service.send_message("❌ El nombre debe tener entre 1 y 120 caracteres.", chat_id=chat_id)
            return

        from src.application.services.lore_harvester_service import LoreHarvesterService, VerifiedLoreConflict

        def _harvest_blocking():
            # Raspado HTTP síncrono + SQL: se ejecuta en un hilo para no congelar el event loop de asyncio.
            with SessionCloud() as db:
                if query_str.isdigit():
                    char = LoreHarvesterService.harvest_for_product(db, int(query_str))
                else:
                    char = LoreHarvesterService.get_or_create_character_lore(db, query_str)
                if not char:
                    return None
                return {
                    "canonical_name": char.canonical_name,
                    "subtitle": char.subtitle,
                    "faction": char.faction,
                    "type_line": char.type_line,
                    "quote": char.quote,
                    "author": char.flavor_quote_author or char.canonical_name,
                    "lore": char.lore,
                }

        try:
            char = await asyncio.to_thread(_harvest_blocking)
        except VerifiedLoreConflict as conflict:
            await telegram_service.send_message(
                f"⚠️ <b>{conflict.slug}</b> ya está verificado. Re-cosecharlo exige confirmación con <code>force</code> desde el panel Grimorio Lore.",
                chat_id=chat_id,
            )
            return

        if char:
            msg = (
                f"📜 <b>[Grimorio de Grayskull: Lore Cosechado]</b>\n\n"
                f"• <b>Nombre:</b> <b>{char['canonical_name']}</b>\n"
                f"• <b>Subtítulo:</b> <i>{char['subtitle'] or 'Campeón de Eternia'}</i>\n"
                f"• <b>Facción:</b> {char['faction']}\n"
                f"• <b>Tipo:</b> {char['type_line']}\n"
                f"• <b>Cita:</b> <i>\"{char['quote'] or 'Por el poder de Grayskull!'}\"</i> — {char['author']}\n"
                f"• <b>Biografía:</b> {char['lore'][:200]}..."
            )
            await telegram_service.send_message(msg, chat_id=chat_id)
        else:
            await telegram_service.send_message(f"❌ No se pudo cosechar lore para '<b>{query_str}</b>'.", chat_id=chat_id)

# Instancia única del listener
telegram_listener = TelegramListener()
