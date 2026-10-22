import asyncio
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import psutil
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, File, UploadFile
from loguru import logger
from sqlalchemy import desc, func

from src.domain.models import ScraperExecutionLogModel, ScraperStatusModel, WallapopIpLogModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import verify_api_key
from src.interfaces.api.schemas import (
    ScraperRunRequest,
    ScraperStatusOutput,
    ScraperExecutionLogOutput,
    RunScraperOutput,
    StopScrapersOutput,
    WallapopIpLogOutput,
    WallapopManualHtmlImportOutput,
)
from typing import List, Optional

router = APIRouter(prefix="/api/scrapers", tags=["scrapers"])

# 🛡️ Flag global de cancelación cooperativa
scraper_cancel_event = threading.Event()

from src.interfaces.api.deps import CANONICAL_SPIDER_NAMES, REGISTERED_SPIDERS


def run_scraper_task(
    spider_name: str = "all",
    trigger_type: str = "manual",
    query: str | None = None,
    log_id: int | None = None,
):
    """Wrapper para ejecutar recolectores y actualizar el estado en BD"""
    scraper_cancel_event.clear()

    # Canonicalizar nombre del spider para evitar duplicidades por mayúsculas/minúsculas
    canonical_spider_name = CANONICAL_SPIDER_NAMES.get(spider_name.lower().strip(), spider_name)

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

    # 1. Marcar inicio en la base de datos y crear Log (si no viene ya creado)
    if not log_id:
        with SessionCloud() as db:
            status = (
                db.query(ScraperStatusModel)
                .filter(func.lower(ScraperStatusModel.spider_name) == canonical_spider_name.lower())
                .first()
            )
            if not status:
                status = ScraperStatusModel(spider_name=canonical_spider_name)
                db.add(status)
            else:
                status.spider_name = canonical_spider_name
            status.status = "running"
            status.start_time = datetime.now(timezone.utc).replace(tzinfo=None)

            execution_log = ScraperExecutionLogModel(
                spider_name=canonical_spider_name,
                status="running",
                start_time=status.start_time,
                trigger_type=trigger_type,
                logs=f"[{datetime.now(ZoneInfo('Europe/Madrid')).strftime('%H:%M:%S')}] 🚀 Desplegando incursión manual: {canonical_spider_name}\n",
            )
            db.add(execution_log)
            db.commit()
            log_id = execution_log.id

    log_lock = threading.Lock()
    log_buffer: list[str] = []
    last_flush = [time.monotonic()]

    def _flush_log_buffer_locked():
        if not log_id or not log_buffer:
            return
        chunk_text = "\n".join(log_buffer)
        log_buffer.clear()
        last_flush[0] = time.monotonic()
        try:
            with SessionCloud() as db_l:
                entry = (
                    db_l.query(ScraperExecutionLogModel)
                    .filter(ScraperExecutionLogModel.id == log_id)
                    .first()
                )
                if entry:
                    if entry.logs:
                        entry.logs += "\n" + chunk_text
                    else:
                        entry.logs = chunk_text
                    db_l.commit()
        except Exception:
            pass

    def flush_live_logs():
        with log_lock:
            _flush_log_buffer_locked()

    def update_live_log(msg: str, force: bool = False):
        if not log_id:
            return
        ts = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        with log_lock:
            log_buffer.append(line)
            now_mono = time.monotonic()
            if force or len(log_buffer) >= 15 or (now_mono - last_flush[0]) >= 2.0:
                _flush_log_buffer_locked()

    update_live_log(f"⚔️ Iniciando secuencia de extracción para {spider_name}...", force=True)

    items_found = 0
    new_items = 0

    try:
        from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
        from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
        from src.infrastructure.scrapers.detoyboys_scraper import DeToyboysNLScraper
        from src.infrastructure.scrapers.dvdstorespain_scraper import DVDStoreSpainScraper
        from src.infrastructure.scrapers.ebay_scraper import EbayScraper
        from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
        from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
        from src.infrastructure.scrapers.frikiverso_scraper import FrikiversoScraper
        from src.infrastructure.scrapers.frikimaz_scraper import FrikimazScraper
        from src.infrastructure.scrapers.lamansiondelterror_scraper import LaMansionDelTerrorScraper
        from src.infrastructure.scrapers.pipeline import ScrapingPipeline
        from src.infrastructure.scrapers.pixelatoy_scraper import PixelatoyScraper
        from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper
        from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper
        from src.infrastructure.scrapers.bixoto_scraper import BixotoScraper
        from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
        from src.infrastructure.scrapers.vinted_scraper import VintedScraper
        from src.infrastructure.scrapers.wallapop_manual_scraper import WallapopManualScraper
        from src.infrastructure.scrapers.triguetech_scraper import TriguetechScraper

        wallapop_instance = WallapopManualScraper()
        spiders_map = {
            "Fantasia Personajes": FantasiaScraper(),
            "Frikiverso": FrikiversoScraper(),
            "Frikimaz": FrikimazScraper(),
            "Electropolis": ElectropolisScraper(),
            "Pixelatoy": PixelatoyScraper(),
            "Amazon.es": AmazonScraper(),
            "DeToyboys": DeToyboysNLScraper(),
            "Ebay.es": EbayScraper(),
            "Vinted": VintedScraper(),
            "Wallapop": wallapop_instance,
            "WallapopManual": wallapop_instance,
            "ToymiEU": ToymiEUScraper(),
            "Bixoto": BixotoScraper(),
            "Time4ActionToysDE": Time4ActionToysDEScraper(),
            "BigBadToyStore": BigBadToyStoreScraper(),
            "SmythsToys": SmythsToysScraper(),
            "DVDStoreSpain": DVDStoreSpainScraper(),
            "Triguetech": TriguetechScraper(),
            "LaMansionDelTerror": LaMansionDelTerrorScraper(),
        }

        lookup_name = canonical_spider_name.lower()
        matching_key = next(
            (k for k in spiders_map.keys() if k.lower() == lookup_name), None
        )

        spiders_to_run = []
        if canonical_spider_name == "all":
            unique_spiders = []
            seen_spiders = set()
            for s in spiders_map.values():
                if s not in seen_spiders:
                    seen_spiders.add(s)
                    unique_spiders.append(s)
            spiders_to_run = unique_spiders
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
            pipeline.log_callback = update_live_log
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            search_term = query or "auto"

            update_live_log(
                f"📡 Buscando reliquias para '{search_term}' en {canonical_spider_name}...",
                force=True,
            )

            try:
                try:
                    results = loop.run_until_complete(
                        asyncio.wait_for(
                            pipeline.run_product_search(search_term), timeout=1800
                        )
                    )
                except asyncio.TimeoutError:
                    update_live_log(
                        "⌛ [TIMEOUT] La incursión ha excedido los 30 minutos. Abortando.",
                        force=True,
                    )
                    results = []

                if scraper_cancel_event.is_set():
                    update_live_log(
                        f"🛑 Incursión cancelada manualmente. {len(results)} ofertas parciales recolectadas.",
                        force=True,
                    )

                update_live_log(f"💾 Persistiendo {len(results)} ofertas...", force=True)
                new_items = pipeline.update_database(
                    results, shop_names=[s.shop_name for s in spiders_to_run]
                )
                new_items = new_items if new_items is not None else 0
                items_found = len(results)
                logger.info(
                    f"💾 Persistidas {items_found} ofertas tras incursión de {canonical_spider_name}."
                )
                update_live_log(
                    f"✅ Incursión completada con éxito. {items_found} reliquias encontradas.",
                    force=True,
                )
            finally:
                flush_live_logs()
                loop.close()

        flush_live_logs()
        with SessionCloud() as db:
            status = (
                db.query(ScraperStatusModel)
                .filter(func.lower(ScraperStatusModel.spider_name) == canonical_spider_name.lower())
                .first()
            )
            if status:
                status.spider_name = canonical_spider_name
                status.status = "completed"
                status.end_time = datetime.now(timezone.utc).replace(tzinfo=None)

            log = (
                db.query(ScraperExecutionLogModel)
                .filter(ScraperExecutionLogModel.id == log_id)
                .first()
            )
            if log:
                log.status = "success"
                log.end_time = datetime.now(timezone.utc).replace(tzinfo=None)
                log.items_found = items_found
                log.new_items = new_items if new_items is not None else 0

            db.commit()

    except Exception as e:
        logger.error(f"Scraper Error ({canonical_spider_name}): {e}")
        update_live_log(f"❌ FALLO CRÍTICO: {str(e)}", force=True)
        flush_live_logs()
        with SessionCloud() as db:
            status = (
                db.query(ScraperStatusModel)
                .filter(func.lower(ScraperStatusModel.spider_name) == canonical_spider_name.lower())
                .first()
            )
            if status:
                status.spider_name = canonical_spider_name
                status.status = f"error: {str(e)}"

            log = (
                db.query(ScraperExecutionLogModel)
                .filter(ScraperExecutionLogModel.id == log_id)
                .first()
            )
            if log:
                log.status = "error"
                log.end_time = datetime.now(timezone.utc).replace(tzinfo=None)
                log.error_message = str(e)

            db.commit()


@router.get("/status", response_model=List[ScraperStatusOutput], dependencies=[Depends(verify_api_key)])
def get_scrapers_status():
    """Retorna el estado actual de los recolectores (Admin Only)"""
    with SessionCloud() as db:
        statuses = (
            db.query(ScraperStatusModel)
            .filter(
                ScraperStatusModel.spider_name.notin_(
                    [
                        "Nexus", "NexusVintage", "Harvester", "harvester", "all",
                        "idealo.es", "Idealo.es", "Amazon", "amazon", "Tradeinn", "tradeinn"
                    ]
                )
            )
            .all()
        )
        unique_statuses = {}
        for s in statuses:
            canonical = CANONICAL_SPIDER_NAMES.get(s.spider_name.lower().strip(), s.spider_name)
            key = canonical.lower()
            if key not in unique_statuses or s.spider_name == canonical:
                s.spider_name = canonical
                unique_statuses[key] = s
        return list(unique_statuses.values())


@router.get("/logs", response_model=List[ScraperExecutionLogOutput], dependencies=[Depends(verify_api_key)])
def get_scrapers_logs():
    """Retorna el historial de ejecuciones (Admin Only)"""
    with SessionCloud() as db:
        return (
            db.query(ScraperExecutionLogModel)
            .order_by(desc(ScraperExecutionLogModel.start_time))
            .limit(75)
            .all()
        )


@router.get("/quota-status", dependencies=[Depends(verify_api_key)])
async def get_github_quota_status():
    """Retorna el estado en vivo de la cuota mensual de GitHub Actions (2.000 min), saldo y reposición."""
    from src.application.services.github_quota_service import GitHubQuotaService
    return await GitHubQuotaService.get_quota_status()


@router.get("/execution-logs/export", dependencies=[Depends(verify_api_key)])
def export_execution_logs_csv():
    """Genera y descarga un archivo CSV con el historial de ejecuciones y minutos facturables."""
    from src.application.services.github_quota_service import GitHubQuotaService
    csv_data = GitHubQuotaService.generate_logs_csv()
    filename = f"oraculo_execution_logs_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/run", response_model=RunScraperOutput, dependencies=[Depends(verify_api_key)])
def run_scrapers(request: ScraperRunRequest, background_tasks: BackgroundTasks):
    """Inicia la recolección de reliquias en segundo plano (Admin Only)"""
    canonical_spider_name = CANONICAL_SPIDER_NAMES.get(
        request.spider_name.lower().strip(), request.spider_name
    )
    with SessionCloud() as db:
        status = (
            db.query(ScraperStatusModel)
            .filter(func.lower(ScraperStatusModel.spider_name) == canonical_spider_name.lower())
            .first()
        )
        if not status:
            status = ScraperStatusModel(spider_name=canonical_spider_name)
            db.add(status)
        else:
            status.spider_name = canonical_spider_name
        status.status = "running"
        status.start_time = datetime.now(timezone.utc).replace(tzinfo=None)

        execution_log = ScraperExecutionLogModel(
            spider_name=canonical_spider_name,
            status="running",
            start_time=status.start_time,
            trigger_type=request.trigger_type,
            logs=f"[{datetime.now(ZoneInfo('Europe/Madrid')).strftime('%H:%M:%S')}] 🚀 Desplegando incursión manual: {canonical_spider_name}\n",
        )
        db.add(execution_log)
        db.commit()
        log_id = execution_log.id

    background_tasks.add_task(
        run_scraper_task, canonical_spider_name, request.trigger_type, request.query, log_id
    )
    return {
        "status": "success",
        "log_id": log_id,
        "message": f"Incursión '{canonical_spider_name}' para '{request.query or 'auto'}' desplegada en los páramos de Eternia",
    }


@router.post("/stop", response_model=StopScrapersOutput, dependencies=[Depends(verify_api_key)])
def stop_scrapers():
    """
    Protocolo de Emergencia: Mata procesos de scrapers activos y resetea estados en BD.
    (Admin Only - URGENTE)
    """
    killed_count = 0
    try:
        scraper_cancel_event.set()
        logger.warning("🚨 CANCEL FLAG SET: Señal de parada enviada al pipeline.")

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

        with SessionCloud() as db:
            db.query(ScraperStatusModel).filter(
                ScraperStatusModel.status == "running"
            ).update({"status": "stopped", "end_time": datetime.now(timezone.utc).replace(tzinfo=None)})

            db.query(ScraperExecutionLogModel).filter(
                ScraperExecutionLogModel.status == "running"
            ).update(
                {
                    "status": "stopped",
                    "end_time": datetime.now(timezone.utc).replace(tzinfo=None),
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


@router.get("/wallapop/ip-logs", response_model=List[WallapopIpLogOutput], dependencies=[Depends(verify_api_key)])
def get_wallapop_ip_logs():
    """Retorna el historial de logs de IP de Wallapop (Admin Only)"""
    with SessionCloud() as db:
        return (
            db.query(WallapopIpLogModel)
            .order_by(desc(WallapopIpLogModel.recorded_at))
            .limit(100)
            .all()
        )


@router.get("/wallapop/ip-logs/download", dependencies=[Depends(verify_api_key)])
def download_wallapop_ip_logs():
    """Descarga los logs de IP de Wallapop en formato TXT (Admin Only)"""
    with SessionCloud() as db:
        logs = (
            db.query(WallapopIpLogModel)
            .order_by(desc(WallapopIpLogModel.recorded_at))
            .limit(500)
            .all()
        )
        
        lines = []
        lines.append("=== AUDITORÍA DE ACCESIBILIDAD IP - SCRAPER WALLAPOP ===")
        lines.append(f"Fecha del Reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total de Intentos Registrados: {len(logs)}")
        lines.append("Este archivo contiene el historial de WAF checks para depurar bloqueos de Cloudflare.")
        lines.append("=" * 80 + "\n")
        
        for idx, log in enumerate(logs, 1):
            recorded_str = log.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if log.recorded_at else "N/A"
            lines.append(f"Registro #{idx} - [{recorded_str}]")
            lines.append(f"  - Dirección IP:  {log.ip_address}")
            lines.append(f"  - Estado:        {log.status.upper()}")
            lines.append(f"  - Entorno:       {log.environment or 'Local'}")
            lines.append(f"  - Código HTTP:   {log.response_code if log.response_code is not None else 'N/A'}")
            lines.append(f"  - Detalles WAF:  {log.details or 'N/A'}")
            lines.append("-" * 80)
            
        content = "\n".join(lines)
        return Response(
            content=content,
            media_type="text/plain",
            headers={
                "Content-Disposition": 'attachment; filename="wallapop_ip_logs.txt"'
            }
        )


@router.post("/wallapop/import-manual-html", response_model=WallapopManualHtmlImportOutput, dependencies=[Depends(verify_api_key)])
async def import_wallapop_manual_html(file: Optional[UploadFile] = File(None)):
    """Parsea el archivo local o subido data/wallapop_search.html e inserta los artículos nuevos en el Purgatorio."""
    import re
    from bs4 import BeautifulSoup
    from src.domain.models import (
        PendingMatchModel,
        OfferModel,
        BlackcludedItemModel,
        VintageMiscellaneousModel
    )

    project_root = os.getcwd()
    file_path = os.path.join(project_root, "data", "wallapop_search.html")
    content = ""

    if file is not None:
        try:
            content_bytes = await file.read()
            content = content_bytes.decode("utf-8", errors="ignore")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar el archivo HTML subido: {str(e)}"
            )
    else:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Archivo 'data/wallapop_search.html' no encontrado en el servidor. Asegúrate de subir el archivo o guardarlo en local."
            )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al leer el archivo HTML local: {str(e)}"
            )

    soup = BeautifulSoup(content, 'html.parser')
    cards = soup.select("a[href*='/item/']")
    
    offers_to_process = []
    seen_urls = set()
    junk_keywords = ["camiseta", "t-shirt", "poster", "taza", "mug", "revista", "dvd", "llavero", "keyring", "reproduccion", "repro", "sticker", "pegatina"]

    for card in cards:
        try:
            price_node = card.select_one("span[class*='Price'], [class*='price']")
            title_node = card.select_one("p[class*='Title'], [class*='title']")
            img_node = card.select_one("img")

            if not price_node or not title_node:
                continue

            title = title_node.get_text(strip=True)
            title_lower = title.lower()
            
            if any(kw in title_lower for kw in junk_keywords):
                continue

            price_text = price_node.get_text(strip=True)
            price_val = float(re.sub(r'[^\d.,]', '', price_text).replace(',', '.'))
            if price_val <= 0:
                continue

            href = card.get("href", "")
            clean_href = href.split("?")[0]
            full_url = clean_href if clean_href.startswith("http") else f"https://es.wallapop.com{clean_href}"

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)
            image_url = img_node.get("src") if img_node else None

            offers_to_process.append({
                "product_name": f"[Wallapop HTML] {title}",
                "price": price_val,
                "url": full_url,
                "image_url": image_url
            })
        except Exception:
            continue

    total_found = len(offers_to_process)
    if total_found == 0:
        return {
            "status": "success",
            "total_found": 0,
            "total_skipped": 0,
            "total_inserted": 0,
            "message": "No se encontraron ofertas válidas de Wallapop en el HTML."
        }

    incoming_urls = [o["url"] for o in offers_to_process]
    saved_count = 0
    skipped_count = 0

    with SessionCloud() as db:
        blocked_urls = set(
            x[0] for x in db.query(BlackcludedItemModel.url).filter(BlackcludedItemModel.url.in_(incoming_urls)).all()
        )
        existing_pending_urls = set(
            x[0] for x in db.query(PendingMatchModel.url).filter(PendingMatchModel.url.in_(incoming_urls)).all()
        )
        existing_offers_urls = set(
            x[0] for x in db.query(OfferModel.url).filter(OfferModel.url.in_(incoming_urls)).all()
        )
        existing_misc_urls = set(
            x[0] for x in db.query(VintageMiscellaneousModel.url).filter(VintageMiscellaneousModel.url.in_(incoming_urls)).all()
        )

        exclusion_set = blocked_urls.union(existing_pending_urls).union(existing_offers_urls).union(existing_misc_urls)

        for offer in offers_to_process:
            if offer["url"] in exclusion_set:
                skipped_count += 1
                continue

            pending = PendingMatchModel(
                scraped_name=offer["product_name"],
                price=offer["price"],
                currency="EUR",
                url=offer["url"],
                shop_name="Wallapop",
                image_url=offer["image_url"],
                source_type="Peer-to-Peer",
                found_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            db.add(pending)
            saved_count += 1

        db.commit()

    return {
        "status": "success",
        "total_found": total_found,
        "total_skipped": skipped_count,
        "total_inserted": saved_count,
        "message": f"Se procesaron {total_found} ofertas. Insertadas: {saved_count}, Omitidas: {skipped_count} (duplicadas/asignadas/descartadas)."
    }
