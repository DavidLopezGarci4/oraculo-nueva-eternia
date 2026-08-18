import asyncio
import httpx
import logging
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
            
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.telegram_chat_id == chat_id_str).first()
            if user:
                is_admin_role = (user.role or "").strip().lower() == "admin" or (user.username or "").strip().lower() in ("david", "admin") or user.id in (1, 2)
                return is_admin_role, True, user
        return False, False, None

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
        elif data == "ssl:status":
            await self.answer_callback_query(cq_id, "🔍 Consultando estado SSL...")
            await self.cmd_ssl_status(chat_id)
        elif data.startswith("device:allow:"):
            if not self.is_sovereign_admin(chat_id):
                await self.answer_callback_query(cq_id, "❌ Acción restringida exclusivamente al Gran Arquitecto.")
                return
            dev_id = int(data.split(":")[2])
            with SessionCloud() as db:
                device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == dev_id).first()
                if not device:
                    await self.answer_callback_query(cq_id, "❌ Dispositivo no encontrado.")
                    return
                device.is_authorized = True
                db.commit()
                dev_name = device.device_name or device.device_id
            await self.answer_callback_query(cq_id, f"✅ Dispositivo '{dev_name}' autorizado.")
            await telegram_service.send_message(
                f"🛡️ <b>[Escudo de Eternia]</b> Dispositivo <b>{dev_name}</b> (<code>{device.device_id}</code>) ha sido <b>AUTORIZADO</b> con éxito.",
                chat_id=chat_id
            )
        elif data.startswith("device:deny:"):
            if not self.is_sovereign_admin(chat_id):
                await self.answer_callback_query(cq_id, "❌ Acción restringida exclusivamente al Gran Arquitecto.")
                return
            dev_id = int(data.split(":")[2])
            with SessionCloud() as db:
                device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == dev_id).first()
                if not device:
                    await self.answer_callback_query(cq_id, "❌ Dispositivo no encontrado.")
                    return
                dev_name = device.device_name or device.device_id
                db.delete(device)
                db.commit()
            await self.answer_callback_query(cq_id, f"🚫 Dispositivo '{dev_name}' bloqueado.")
            await telegram_service.send_message(
                f"🛑 <b>[Escudo de Eternia]</b> Dispositivo <b>{dev_name}</b> ha sido <b>BLOQUEADO Y ELIMINADO</b>.",
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
        if not text.startswith("/"):
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
            
        # --- Comandos de Administrador Only ---
        elif is_admin:
            if command == "/status":
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
            await telegram_service.send_message("❌ Uso: <code>/register [nombre_usuario]</code>", chat_id=chat_id)
            return
            
        username = args[0].strip()
        with SessionCloud() as db:
            db_user = db.query(UserModel).filter(UserModel.username == username).first()
            if not db_user:
                await telegram_service.send_message(f"❌ Usuario <b>{username}</b> no encontrado en el sistema.", chat_id=chat_id)
                return
                
            chat_id_str = str(chat_id)
            if db_user.telegram_chat_id and db_user.telegram_chat_id != chat_id_str:
                await telegram_service.send_message("❌ Este usuario ya tiene otro chat ID asociado.", chat_id=chat_id)
                return
                
            db_user.telegram_chat_id = chat_id_str
            db.commit()
            
            msg = (
                f"<b>✅ Registro Exitoso</b>\n\n"
                f"Bienvenido, Guardián <b>{db_user.username}</b>. Tu chat ID ha sido vinculado.\n"
                f"A partir de ahora recibirás alertas de tu lista de deseos y tus alertas de precios configuradas."
            )
            await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_help(self, chat_id: int, is_admin: bool):
        lines = ["<b>📖 Comandos del Oráculo de Eternia</b>\n"]
        lines.append("<b>Comunes:</b>")
        lines.append("• <code>/purgatorio</code> - Muestra ofertas pendientes de clasificar.")
        lines.append("• <code>/buscar [figura]</code> - Busca ofertas activas en la base de datos.")
        lines.append("• <code>/wallapop [enlace]</code> - Importa un artículo de Wallapop al Purgatorio (o comparte el link directo).")
        lines.append("• <code>/help</code> - Muestra este menú de ayuda.")
        
        if is_admin:
            lines.append("\n<b>Administrador / Soberano Only:</b>")
            lines.append("• <code>/status</code> - Consulta de salud del sistema, scrapers y base de datos.")
            lines.append("• <code>/ssl</code> - Diagnóstico en vivo y telemetría de certificados SSL.")
            lines.append("• <code>/renew_ssl</code> - Forzar renovación inmediata de certificados SSL.")
            lines.append("• <code>/tokens</code> - Comprobación en vivo de Apify y ScraperAPI (0 créditos).")
            lines.append("• <code>/nexus</code> - Incursión rápida de novedades Wallapop (Tríada Core).")
            lines.append("• <code>/nexus completo</code> - Incursión profunda (5 familias + paginación escalonada).")
            lines.append("• <code>/nexus [consulta]</code> - Búsqueda personalizada en Wallapop.")
            lines.append("• <code>/devices</code> - Listar y gestionar dispositivos con botones de aprobación.")
            lines.append("• <code>/approve [id]</code> - Autorizar acceso a un dispositivo.")
            lines.append("• <code>/deny [id]</code> - Bloquear/eliminar un dispositivo.")
            lines.append("• <code>/run [tienda] [búsqueda]</code> - Lanza un recolector en segundo plano (ej: <code>/run wallapop heman</code>).")
            lines.append("• <code>/stop</code> - Protocolo de parada de emergencia para detener scrapers.")
            
        await telegram_service.send_message("\n".join(lines), chat_id=chat_id)

    async def cmd_purgatorio(self, chat_id: int):
        with SessionCloud() as db:
            total = db.query(PendingMatchModel).count()
            vintage = db.query(PendingMatchModel).filter(PendingMatchModel.is_vintage == True).count()
            modern = db.query(PendingMatchModel).filter(PendingMatchModel.is_vintage == False).count()
            high_opp = db.query(PendingMatchModel).filter(PendingMatchModel.opportunity_score >= 80).count()
            
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
            
        with SessionCloud() as db:
            # Búsqueda insensible a mayúsculas
            search_query = f"%{query}%"
            offers = db.query(OfferModel).join(ProductModel).filter(
                OfferModel.is_available == True,
                ProductModel.name.like(search_query)
            ).order_by(OfferModel.price).limit(5).all()
            
        if not offers:
            await telegram_service.send_message(f"🔍 No se encontraron ofertas activas para <b>'{query}'</b>.", chat_id=chat_id)
            return
            
        lines = [f"<b>🔍 Top 5 Ofertas más baratas para '{query}':</b>\n"]
        for o in offers:
            lines.append(
                f"• <b>{o.product.name}</b>\n"
                f"  💰 {o.price:.2f}€ | 🏪 {o.shop_name}\n"
                f"  🔗 <a href='{o.url}'>Ver Oferta en Web</a>\n"
            )
        await telegram_service.send_message("\n".join(lines), chat_id=chat_id)

    async def cmd_status(self, chat_id: int):
        with SessionCloud() as db:
            # Scrapers status
            statuses = db.query(ScraperStatusModel).all()
            
            # DB Stats
            total_products = db.query(ProductModel).count()
            total_offers = db.query(OfferModel).filter(OfferModel.is_available == True).count()
            
        scraper_lines = []
        for s in statuses:
            icon = "🟢" if s.status == "completed" else "🔴" if "error" in s.status else "⏳" if s.status == "running" else "⚪"
            scraper_lines.append(f"{icon} <b>{s.spider_name}:</b> {s.status.upper()}")
            
        msg = (
            f"<b>📊 Estado del Sistema</b>\n\n"
            f"📚 <b>Catálogo de Productos:</b> {total_products}\n"
            f"🏷️ <b>Ofertas Activas Disponibles:</b> {total_offers}\n\n"
            f"🤖 <b>Estado de Recolectores:</b>\n" + "\n".join(scraper_lines)
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

    async def cmd_run(self, chat_id: int, scraper_name: str, query: Optional[str]):
        # Validar tienda
        valid_spiders = ["fantasia", "frikiverso", "frikimaz", "electropolis", "pixelatoy", "amazon", "detoyboys", "ebay", "vinted", "wallapop", "toymieu", "time4actiontoysde", "bigbadtoystore", "smythstoys", "dvdstorespain", "triguetech", "all"]
        
        if scraper_name.lower() not in valid_spiders:
            await telegram_service.send_message(f"❌ Tienda <b>'{scraper_name}'</b> no válida.\nOpciones: {', '.join(valid_spiders)}", chat_id=chat_id)
            return
            
        # Lanzar tarea
        from fastapi import BackgroundTasks
        bg_tasks = BackgroundTasks()
        bg_tasks.add_task(run_scraper_task, scraper_name, "telegram", query)
        
        # Nota: La ejecución en FastAPI BackgroundTasks requiere la llamada a través del framework,
        # pero aquí podemos ejecutarlo directamente en un thread/ejecutor de asyncio para no requerir fastapi endpoints:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, run_scraper_task, scraper_name, "telegram", query)
        
        await telegram_service.send_message(
            f"🚀 <b>Incursión Iniciada</b>\n\n"
            f"Scraper <b>{scraper_name}</b> ejecutándose en segundo plano para <b>'{query or 'auto'}'</b>.\n"
            f"Te avisaré si detectamos compras obligatorias o alertas de wishlist.", 
            chat_id=chat_id
        )

    async def cmd_stop(self, chat_id: int):
        try:
            # Ejecutar parada
            res = await stop_scrapers()
            killed = res.get("killed_processes", 0)
            await telegram_service.send_message(
                f"🛑 <b>Parada de Emergencia Completada</b>\n\n"
                f"Se han eliminado <b>{killed}</b> procesos de scrapers activos y purificado los estados en base de datos.",
                chat_id=chat_id
            )
        except Exception as e:
            await telegram_service.send_message(f"❌ Error al detener los scrapers: {e}", chat_id=chat_id)

    async def cmd_ssl_status(self, chat_id: int):
        from src.application.services.ssl_service import SSLService
        status = SSLService.get_certificate_status()
        
        icon = "🟢" if status.get("status") == "ACTIVE" else "🟡" if status.get("status") == "EXPIRING_SOON" else "🔴"
        valid_from = status.get("valid_from")
        valid_until = status.get("valid_until")
        next_renewal = status.get("next_renewal_recommended")
        
        from_str = valid_from.strftime("%d/%m/%Y %H:%M UTC") if valid_from else "N/D"
        until_str = valid_until.strftime("%d/%m/%Y %H:%M UTC") if valid_until else "N/D"
        next_str = next_renewal.strftime("%d/%m/%Y") if next_renewal else "N/D"
        
        msg = (
            f"🔒 <b>[Oráculo SSL] Diagnóstico de Certificados</b>\n\n"
            f"• Dominio: <code>{status.get('domain')}</code>\n"
            f"• Estado: {icon} <b>{status.get('status')}</b> ({status.get('days_remaining')} días restantes)\n"
            f"• Emisor: <b>{status.get('issuer')}</b>\n"
            f"• Emisión: <code>{from_str}</code>\n"
            f"• Caducidad: <code>{until_str}</code>\n"
            f"• Próxima Renovación Recomendada: <b>{next_str}</b>\n\n"
            f"ℹ️ <i>{status.get('details')}</i>"
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

        with SessionCloud() as db:
            devices = db.query(AuthorizedDeviceModel).order_by(AuthorizedDeviceModel.id.desc()).limit(15).all()

        if not devices:
            await telegram_service.send_message("🛡️ <b>[Escudo de Eternia]</b> No hay dispositivos registrados en la base de datos.", chat_id=chat_id)
            return

        lines = ["🛡️ <b>[Escudo de Eternia] Dispositivos Registrados:</b>\n"]
        buttons = []

        for d in devices:
            status_icon = "🟢" if d.is_authorized else "🔴"
            status_text = "AUTORIZADO" if d.is_authorized else "BLOQUEADO"
            name = d.device_name or "Sin Nombre"
            lines.append(f"{status_icon} <b>#{d.id} {name}</b> - {status_text}\n  🆔 <code>{d.device_id[:16]}...</code>")

            if not d.is_authorized:
                buttons.append([
                    {"text": f"✅ Aprobar #{d.id} ({name[:12]})", "callback_data": f"device:allow:{d.id}"},
                    {"text": f"🗑️ Eliminar #{d.id}", "callback_data": f"device:deny:{d.id}"}
                ])
            else:
                buttons.append([
                    {"text": f"🚫 Revocar/Eliminar #{d.id} ({name[:12]})", "callback_data": f"device:deny:{d.id}"}
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
        with SessionCloud() as db:
            device = None
            if target.isdigit():
                device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == int(target)).first()
            if not device:
                device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id.like(f"%{target}%")).first()
            
            if not device:
                await telegram_service.send_message(f"❌ No se encontró ningún dispositivo para '<b>{target}</b>'.", chat_id=chat_id)
                return
            
            device.is_authorized = True
            db.commit()
            dev_name = device.device_name or device.device_id
            
        await telegram_service.send_message(
            f"✅ <b>[Escudo de Eternia]</b> Dispositivo <b>{dev_name}</b> (<code>{device.device_id}</code>) ha sido <b>AUTORIZADO</b> permanentemente.",
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
        with SessionCloud() as db:
            device = None
            if target.isdigit():
                device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.id == int(target)).first()
            if not device:
                device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id.like(f"%{target}%")).first()
            
            if not device:
                await telegram_service.send_message(f"❌ No se encontró ningún dispositivo para '<b>{target}</b>'.", chat_id=chat_id)
                return
            
            dev_name = device.device_name or device.device_id
            db.delete(device)
            db.commit()
            
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

            # Relevancia MOTU
            is_relevant, reason = validate_motu_relevance(title)
            if not is_relevant:
                await telegram_service.send_message(
                    f"⚠️ <b>Artículo descartado por filtro MOTU:</b>\n"
                    f"• <b>Título:</b> {title}\n"
                    f"• <i>Motivo: {reason}</i>",
                    chat_id=chat_id
                )
                return

            with SessionCloud() as db:
                existing_p = db.query(PendingMatchModel).filter(PendingMatchModel.url == url).first()
                existing_o = db.query(OfferModel).filter(OfferModel.url == url).first()

                if existing_p or existing_o:
                    await telegram_service.send_message(
                        f"ℹ️ El artículo <b>{title}</b> ({price} €) ya existe en la base de datos del Oráculo.",
                        chat_id=chat_id
                    )
                    return

                new_pending = PendingMatchModel(
                    scraped_name=title,
                    price=float(price) if price else 0.0,
                    url=url,
                    shop_name="Wallapop",
                    image_url=image_url,
                    source_type="Peer-to-Peer",
                    sale_type="Fixed_P2P"
                )
                db.add(new_pending)
                db.commit()

            msg = (
                f"🎁 <b>[Wallapop: Importación Exitosa]</b>\n\n"
                f"• <b>Artículo:</b> {title}\n"
                f"• <b>Precio:</b> <b>{price} €</b>\n"
                f"• <b>Enlace:</b> <a href=\"{url}\">Ver en Wallapop</a>\n\n"
                f"✅ <i>Añadido al Purgatorio del Oráculo para revisión y matching.</i>"
            )
            await telegram_service.send_message(msg, chat_id=chat_id)

        except Exception as e:
            logger.error(f"Error al importar producto de Wallapop desde Telegram: {e}")
            await telegram_service.send_message(f"❌ Error al procesar el enlace: {e}", chat_id=chat_id)

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
        from src.domain.models import WallapopJobModel
        q_clean = query_term.strip().lower()
        if q_clean in ["completo", "full", "deep", "exhaustivo"]:
            job_desc = "🌟 <b>Incursión Profunda Escalonada</b> (5 Familias MOTU Origins + 2 Páginas de Profundidad)"
            target_query = "completo"
            cadence_note = "⏳ <i>Duración estimada: ~1.5 - 2.5 min (Pausas orgánicas entre consultas para 0% detección).</i>"
        elif q_clean in ["auto", "basico", "basic", ""]:
            job_desc = "⚡ <b>Incursión Rápida de Novedades</b> (Tríada Canónica: ~120 ofertas)"
            target_query = "auto"
            cadence_note = "⚡ <i>Duración estimada: ~3 - 5 seg.</i>"
        else:
            job_desc = f"🎯 <b>Búsqueda Personalizada:</b> '<code>{query_term}</code>'"
            target_query = query_term
            cadence_note = "⚡ <i>Duración estimada: ~3 - 10 seg.</i>"

        with SessionCloud() as db:
            job = WallapopJobModel(query=target_query, status="pending")
            db.add(job)
            db.commit()
            db.refresh(job)
            job_id = job.id

        msg = (
            f"⚡ <b>[Nexus Local Bridge]</b> Trabajo <b>#{job_id}</b> encolado.\n\n"
            f"• <b>Modo:</b> {job_desc}\n"
            f"• <b>Destino:</b> El Purgatorio del Oráculo\n"
            f"• {cadence_note}\n\n"
            f"🖥️ <i>Tu PC de casa (con opción [3] de <code>oraculo.ps1</code>) lo procesará con tu IP residencial limpia.</i>"
        )
        await telegram_service.send_message(msg, chat_id=chat_id)

# Instancia única del listener
telegram_listener = TelegramListener()

