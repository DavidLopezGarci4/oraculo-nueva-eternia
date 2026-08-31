import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from loguru import logger
import httpx

from src.core.config import settings
from src.infrastructure.services.telegram_service import telegram_service

class VintedSentinelService:
    """
    Servicio de Centinela Autónomo para Vinted.
    Ejecuta incursiones periódicas con intervalos pseudoaleatorios (50-75 min),
    invocando workflows efímeros en Microsoft Azure vía GitHub Actions API (o fallback local),
    evitando solapamientos con el Daily Scan y despachando reportes interactivos a Telegram.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VintedSentinelService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.is_running: bool = False
        self.current_task: Optional[asyncio.Task] = None
        self.last_run: Optional[datetime] = None
        self.next_run_eta: Optional[datetime] = None
        self.next_delay_minutes: int = 60
        self.total_hunts_executed: int = 0
        self.total_bargains_found: int = 0
        self.last_stats: Optional[Dict[str, Any]] = None

    def start(self):
        """Inicia el bucle centinela en segundo plano si no está corriendo."""
        if self.is_running and self.current_task and not self.current_task.done():
            logger.info("🛡️ VintedSentinel: Ya se encuentra en ejecución.")
            return

        self.is_running = True
        self.current_task = asyncio.create_task(self._sentinel_loop())
        logger.info("🛡️ VintedSentinel: Centinela autónomo INICIADO.")

    def stop(self):
        """Detiene el bucle centinela."""
        self.is_running = False
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None
        self.next_run_eta = None
        logger.info("🛡️ VintedSentinel: Centinela autónomo DETENIDO.")

    def get_status(self) -> Dict[str, Any]:
        """Devuelve el estado operativo actual del Centinela."""
        now = datetime.now(timezone.utc)
        mins_remaining = 0
        if self.next_run_eta and self.next_run_eta > now:
            mins_remaining = max(1, int((self.next_run_eta - now).total_seconds() / 60))

        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run_eta": self.next_run_eta.isoformat() if self.next_run_eta else None,
            "next_run_in_minutes": mins_remaining,
            "total_hunts": self.total_hunts_executed,
            "total_bargains": self.total_bargains_found,
            "using_github_dispatch": bool(settings.GITHUB_TOKEN),
            "github_repo": settings.GITHUB_REPOSITORY,
            "last_stats": self.last_stats,
        }

    def _is_daily_scan_blackout(self, dt: datetime) -> bool:
        """
        Determina si el momento actual coincide con la ventana de exclusión del Daily Scan:
        - 02:00 UTC (01:50 - 02:25 UTC)
        - 14:30 UTC (14:20 - 14:55 UTC)
        """
        hour = dt.hour
        minute = dt.minute

        # Ventana nocturna 02:00 UTC
        if (hour == 1 and minute >= 50) or (hour == 2 and minute <= 25):
            return True

        # Ventana vespertina 14:30 UTC
        if (hour == 14 and minute >= 20 and minute <= 55):
            return True

        return False

    async def _sentinel_loop(self):
        """Bucle principal asíncrono con temporizador dinámico."""
        logger.info("🛡️ VintedSentinel: Bucle de vigilancia activado.")
        
        while self.is_running:
            try:
                # 1. Calcular delay aleatorio entre MIN y MAX (ej: 100 a 120 min)
                min_delay = getattr(settings, "VINTED_SENTINEL_MIN_DELAY_MIN", 100)
                max_delay = getattr(settings, "VINTED_SENTINEL_MAX_DELAY_MIN", 120)
                self.next_delay_minutes = random.randint(min_delay, max_delay)
                self.next_run_eta = datetime.now(timezone.utc) + timedelta(minutes=self.next_delay_minutes)
                
                logger.info(
                    f"🛡️ VintedSentinel: Próxima incursión programada en {self.next_delay_minutes} minutos "
                    f"(ETA: {self.next_run_eta.strftime('%H:%M:%S UTC')})."
                )

                # 2. Dormir el intervalo aleatorio
                await asyncio.sleep(self.next_delay_minutes * 60)

                if not self.is_running:
                    break

                # 3. Comprobar ventana de exclusión del Daily Scan
                now = datetime.now(timezone.utc)
                if self._is_daily_scan_blackout(now):
                    logger.warning("🛡️ VintedSentinel: Coincidencia con ventana del Daily Scan. Pospone 15 min.")
                    await asyncio.sleep(15 * 60)
                    if not self.is_running:
                        break

                # 4. Disparar la incursión
                await self.dispatch_hunt()

            except asyncio.CancelledError:
                logger.info("🛡️ VintedSentinel: Tarea cancelada limpiamente.")
                break
            except Exception as e:
                logger.error(f"🛡️ VintedSentinel: Error en bucle centinela: {e}")
                await asyncio.sleep(60)

    async def dispatch_hunt(self, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Dispara la incursión:
        - Si hay GITHUB_TOKEN: Invoca el workflow efímero de GitHub Actions en Azure.
        - Si no hay token o la API falla: Ejecuta el servicio local VintedHunterService.
        """
        self.last_run = datetime.now(timezone.utc)
        self.total_hunts_executed += 1
        target_chat = chat_id or str(settings.TELEGRAM_CHAT_ID or "")

        # 1. Intento vía GitHub Actions API (Microsoft Azure Runner)
        if settings.GITHUB_TOKEN and settings.GITHUB_REPOSITORY:
            logger.info("🛡️ VintedSentinel: Despachando runner efímero en Microsoft Azure vía GitHub Actions...")
            try:
                headers = {
                    "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                url = f"https://api.github.com/repos/{settings.GITHUB_REPOSITORY}/actions/workflows/vinted_hunter.yml/dispatches"
                payload = {
                    "ref": "main",
                    "inputs": {
                        "query": "auto",
                        "chat_id": target_chat
                    }
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 204:
                        logger.success("🚀 VintedSentinel: Workflow de Azure despachado con éxito (HTTP 204).")
                        res = {"status": "dispatched_to_azure", "mode": "github_actions"}
                        self.last_stats = res
                        return res
                    else:
                        logger.warning(f"⚠️ VintedSentinel: GitHub dispatch devolvió HTTP {resp.status_code}: {resp.text}. Ejecutando fallback local.")
            except Exception as ex:
                logger.error(f"❌ VintedSentinel: Error al conectar con GitHub API: {ex}. Ejecutando fallback local.")

        # 2. Fallback / Ejecución Local directa
        logger.info("🛡️ VintedSentinel: Ejecutando incursión mediante motor asíncrono local...")
        from src.application.services.vinted_hunter_service import VintedHunterService
        try:
            res = await VintedHunterService.run_hunt(
                query="auto",
                chat_id=target_chat,
                notify_summary=True,
                next_eta_mins=self.next_delay_minutes
            )
            self.total_bargains_found += res.get("bargains_found", 0)
            self.last_stats = res
            return res
        except Exception as ex:
            logger.error(f"❌ VintedSentinel: Error en ejecución local de VintedHunter: {ex}")
            return {"status": "error", "error": str(ex)}

vinted_sentinel = VintedSentinelService()
