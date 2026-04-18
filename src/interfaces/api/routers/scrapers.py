import asyncio
import os
import threading
from datetime import datetime, timedelta

import psutil
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from loguru import logger
from sqlalchemy import desc

from src.domain.models import ScraperExecutionLogModel, ScraperStatusModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key
from src.interfaces.api.schemas import ScraperRunRequest

router = APIRouter(prefix="/api/scrapers", tags=["scrapers"])

# 🛡️ Flag global de cancelación cooperativa
scraper_cancel_event = threading.Event()


def run_scraper_task(
    spider_name: str = "all",
    trigger_type: str = "manual",
    query: str | None = None,
):
    """Wrapper para ejecutar recolectores y actualizar el estado en BD"""
    scraper_cancel_event.clear()

    # PHASE 42: PURGE OLD LOGS (7 DAYS)
    try:
        cutoff = datetime.now() - timedelta(days=7)
        with SessionCloud() as db_purge:
            db_purge.query(ScraperExecutionLogModel).filter(
                ScraperExecutionLogModel.start_time < cutoff
            ).delete()
            db_purge.commit()
    except Exception as e:
        logger.warning(f"⚠️ Log purge failed: {e}")

    # 1. Marcar inicio en la base de datos y crear Log
    with SessionCloud() as db:
        status = (
            db.query(ScraperStatusModel)
            .filter(ScraperStatusModel.spider_name == spider_name)
            .first()
        )
        if not status:
            status = ScraperStatusModel(spider_name=spider_name)
            db.add(status)
        status.status = "running"
        status.start_time = datetime.utcnow()

        execution_log = ScraperExecutionLogModel(
            spider_name=spider_name,
            status="running",
            start_time=status.start_time,
            trigger_type=trigger_type,
            logs=f"[{datetime.utcnow().strftime('%H:%M:%S')}] 🚀 Desplegando incursión manual: {spider_name}\n",
        )
        db.add(execution_log)
        db.commit()
        log_id = execution_log.id

    def update_live_log(msg: str):
        if not log_id:
            return
        try:
            with SessionCloud() as db_l:
                entry = db_l.query(ScraperExecutionLogModel).get(log_id)
                if entry:
                    ts = datetime.utcnow().strftime("%H:%M:%S")
                    line = f"[{ts}] {msg}"
                    if entry.logs:
                        entry.logs += "\n" + line
                    else:
                        entry.logs = line
                    db_l.commit()
        except Exception:
            pass

    update_live_log(f"⚔️ Iniciando secuencia de extracción para {spider_name}...")

    items_found = 0

    try:
        from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
        from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
        from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
        from src.infrastructure.scrapers.detoyboys_scraper import DeToyboysNLScraper
        from src.infrastructure.scrapers.dvdstorespain_scraper import DVDStoreSpainScraper
        from src.infrastructure.scrapers.ebay_scraper import EbayScraper
        from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
        from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
        from src.infrastructure.scrapers.frikiverso_scraper import FrikiversoScraper
        from src.infrastructure.scrapers.pipeline import ScrapingPipeline
        from src.infrastructure.scrapers.pixelatoy_scraper import PixelatoyScraper
        from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper
        from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper
        from src.infrastructure.scrapers.tradeinn_scraper import TradeinnScraper
        from src.infrastructure.scrapers.vinted_scraper import VintedScraper
        from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper

        spiders_map = {
            "ActionToys": ActionToysScraper(),
            "Fantasia Personajes": FantasiaScraper(),
            "Frikiverso": FrikiversoScraper(),
            "Electropolis": ElectropolisScraper(),
            "Pixelatoy": PixelatoyScraper(),
            "Amazon.es": AmazonScraper(),
            "DeToyboys": DeToyboysNLScraper(),
            "Ebay.es": EbayScraper(),
            "Vinted": VintedScraper(),
            "Wallapop": WallapopScraper(),
            "ToymiEU": ToymiEUScraper(),
            "Time4ActionToysDE": Time4ActionToysDEScraper(),
            "BigBadToyStore": BigBadToyStoreScraper(),
            "Tradeinn": TradeinnScraper(),
            "DVDStoreSpain": DVDStoreSpainScraper(),
        }

        lookup_name = spider_name.lower()
        matching_key = next(
            (k for k in spiders_map.keys() if k.lower() == lookup_name), None
        )

        spiders_to_run = []
        if spider_name == "all":
            spiders_to_run = list(spiders_map.values())
        elif matching_key:
            s = spiders_map[matching_key]
            s.log_callback = update_live_log
            spiders_to_run = [s]

        if spiders_to_run:
            for s in spiders_to_run:
                s.log_callback = update_live_log

            pipeline = ScrapingPipeline(
                spiders_to_run, cancel_event=scraper_cancel_event
            )
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # PHASE 47: Use provided query or fallback to specific store defaults
            search_term = query
            if not search_term:
                search_term = (
                    "masters of the universe origins"
                    if spider_name.lower() == "tradeinn"
                    else "auto"
                )

            update_live_log(
                f"📡 Buscando reliquias para '{search_term}' en {spider_name}..."
            )

            try:
                results = loop.run_until_complete(
                    asyncio.wait_for(
                        pipeline.run_product_search(search_term), timeout=1800
                    )
                )
            except asyncio.TimeoutError:
                update_live_log(
                    "⌛ [TIMEOUT] La incursión ha excedido los 30 minutos. Abortando."
                )
                results = []

            loop.close()

            if scraper_cancel_event.is_set():
                update_live_log(
                    f"🛑 Incursión cancelada manualmente. {len(results)} ofertas parciales recolectadas."
                )

            update_live_log(f"💾 Persistiendo {len(results)} ofertas...")
            pipeline.update_database(
                results, shop_names=[s.shop_name for s in spiders_to_run]
            )
            items_found = len(results)
            logger.info(
                f"💾 Persistidas {items_found} ofertas tras incursión de {spider_name}."
            )
            update_live_log(
                f"✅ Incursión completada con éxito. {items_found} reliquias encontradas."
            )

        with SessionCloud() as db:
            status = (
                db.query(ScraperStatusModel)
                .filter(ScraperStatusModel.spider_name == spider_name)
                .first()
            )
            if status:
                status.status = "completed"
                status.end_time = datetime.utcnow()

            log = (
                db.query(ScraperExecutionLogModel)
                .filter(ScraperExecutionLogModel.id == log_id)
                .first()
            )
            if log:
                log.status = "success"
                log.end_time = datetime.utcnow()
                log.items_found = items_found

            db.commit()

    except Exception as e:
        logger.error(f"Scraper Error ({spider_name}): {e}")
        update_live_log(f"❌ FALLO CRÍTICO: {str(e)}")
        with SessionCloud() as db:
            status = (
                db.query(ScraperStatusModel)
                .filter(ScraperStatusModel.spider_name == spider_name)
                .first()
            )
            if status:
                status.status = f"error: {str(e)}"

            log = (
                db.query(ScraperExecutionLogModel)
                .filter(ScraperExecutionLogModel.id == log_id)
                .first()
            )
            if log:
                log.status = "error"
                log.end_time = datetime.utcnow()
                log.error_message = str(e)

            db.commit()


@router.get("/status", dependencies=[Depends(verify_api_key)])
async def get_scrapers_status():
    """Retorna el estado actual de los recolectores (Admin Only)"""
    with SessionCloud() as db:
        return (
            db.query(ScraperStatusModel)
            .filter(
                ScraperStatusModel.spider_name.notin_(
                    ["Nexus", "Harvester", "harvester", "all", "idealo.es", "Idealo.es"]
                )
            )
            .all()
        )


@router.get("/logs", dependencies=[Depends(verify_api_key)])
async def get_scrapers_logs():
    """Retorna el historial de ejecuciones (Admin Only)"""
    with SessionCloud() as db:
        return (
            db.query(ScraperExecutionLogModel)
            .order_by(desc(ScraperExecutionLogModel.start_time))
            .limit(75)
            .all()
        )


@router.post("/run", dependencies=[Depends(verify_api_key)])
async def run_scrapers(request: ScraperRunRequest, background_tasks: BackgroundTasks):
    """Inicia la recolección de reliquias en segundo plano (Admin Only)"""
    background_tasks.add_task(
        run_scraper_task, request.spider_name, request.trigger_type, request.query
    )
    return {
        "status": "success",
        "message": f"Incursión '{request.spider_name}' para '{request.query or 'auto'}' desplegada en los páramos de Eternia",
    }


@router.post("/stop", dependencies=[Depends(verify_api_key)])
async def stop_scrapers():
    """
    Protocolo de Emergencia: Mata procesos de scrapers activos y resetea estados en BD.
    (Admin Only - URGENTE)
    """
    killed_count = 0
    try:
        # 0. Software Stop: Señal cooperativa de cancelación
        scraper_cancel_event.set()
        logger.warning("🚨 CANCEL FLAG SET: Señal de parada enviada al pipeline.")

        # 1. Hardware Stop: Matar procesos hijos (Playwright/Browsers)
        current_process = psutil.Process(os.getpid())
        children = current_process.children(recursive=True)

        target_keywords = ["playwright", "chromium", "chrome", "node", "python"]

        for child in children:
            try:
                cmdline = " ".join(child.cmdline()).lower()
                if any(kw in cmdline for kw in target_keywords):
                    logger.warning(
                        f"🚨 KILLING SCRAPER PROCESS: {child.pid} ({cmdline[:50]}...)"
                    )
                    child.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 2. Database Reset: Limpiar estados de 'running'
        with SessionCloud() as db:
            db.query(ScraperStatusModel).filter(
                ScraperStatusModel.status == "running"
            ).update({"status": "stopped", "end_time": datetime.utcnow()})

            db.query(ScraperExecutionLogModel).filter(
                ScraperExecutionLogModel.status == "running"
            ).update(
                {
                    "status": "stopped",
                    "end_time": datetime.utcnow(),
                    "error_message": "PARADA DE EMERGENCIA: Acción forzada por el Arquitecto",
                }
            )

            db.commit()

        logger.success(
            f"🛑 Scrapers detenidos. {killed_count} procesos eliminados. BD purificada."
        )
        return {
            "status": "success",
            "message": f"Justicia de Eternia: {killed_count} procesos purgados y sistemas reseteados.",
            "killed_processes": killed_count,
        }

    except Exception as e:
        logger.error(f"Error en Protocolo de Emergencia: {e}")
        raise HTTPException(
            status_code=500, detail=f"Fallo en el protocolo de parada: {str(e)}"
        )
