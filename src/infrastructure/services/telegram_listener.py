import asyncio
import httpx
import logging
import re
from typing import Optional
from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel, ScraperStatusModel, PendingMatchModel, OfferModel, ProductModel
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

    async def get_user_status(self, chat_id: int) -> tuple[bool, bool, Optional[UserModel]]:
        """Devuelve (is_admin, is_guardian, user_obj)."""
        chat_id_str = str(chat_id)
        if chat_id_str == str(self.admin_chat_id):
            return True, True, None
            
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.telegram_chat_id == chat_id_str).first()
            if user:
                is_admin = user.role == "admin"
                return is_admin, True, user
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
                            message = u.get("message", {})
                            await self.process_message(message)
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
        
        # Solo procesar comandos que inicien con '/'
        if not text.startswith("/"):
            return
            
        # Comprobar roles y permisos
        is_admin, is_guardian, user = await self.get_user_status(chat_id)
        
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
            
        # --- Comandos de Administrador Only ---
        elif is_admin:
            if command == "/status":
                await self.cmd_status(chat_id)
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
        lines.append("• <code>/help</code> - Muestra este menú de ayuda.")
        
        if is_admin:
            lines.append("\n<b>Administrador Only:</b>")
            lines.append("• <code>/status</code> - Consulta de salud del sistema, scrapers y base de datos.")
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
        valid_spiders = ["fantasia", "frikiverso", "frikimaz", "electropolis", "pixelatoy", "amazon", "detoyboys", "ebay", "vinted", "wallapop", "toymieu", "time4actiontoysde", "bigbadtoystore", "dvdstorespain", "triguetech", "all"]
        
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

# Instancia única del listener
telegram_listener = TelegramListener()
