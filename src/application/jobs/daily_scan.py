import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
# from vec3.dev.adapters import initialize_runtime, create_db_backup, manage_pid, check_stop_signal, save_json_report

# Initialize 3OX Runtime (Force UTF-8, Path Resolution)
# root_path = initialize_runtime()

from src.core.logger import setup_logging
from loguru import logger
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
# ... (rest of imports)

# New Refactored Scrapers
from src.infrastructure.scrapers.frikimaz_scraper import FrikimazScraper
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.frikiverso_scraper import FrikiversoScraper
from src.infrastructure.scrapers.pixelatoy_scraper import PixelatoyScraper
from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper
from src.infrastructure.scrapers.triguetech_scraper import TriguetechScraper
from src.infrastructure.scrapers.lamansiondelterror_scraper import LaMansionDelTerrorScraper

# Phase 8.4: European Expansion Scrapers
from src.infrastructure.scrapers.detoyboys_scraper import DeToyboysNLScraper

# Phase 8.4b: Advanced Expansion Scrapers
from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper
from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper
from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.infrastructure.scrapers.ebay_scraper import EbayScraper
from src.infrastructure.scrapers.vinted_scraper import VintedScraper
# from src.infrastructure.scrapers.tradeinn_scraper import TradeinnScraper
from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper
from src.application.services.nexus_service import NexusService

# Domain & Infra Models
from src.infrastructure.database_cloud import SessionCloud as SessionLocal # Unified for Cloud
from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel, ProductModel, CollectionItemModel, LogisticRuleModel
from src.core.audit_logger import AuditLogger
from src.core.notifier import NotifierService
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService

async def run_daily_scan(progress_callback=None):
    os.environ["DAILY_SCAN_RUN"] = "true"
    # Ensure logging is set up
    # setup_logging() # Already called at module level or by importer
    logger.info("🚀 Starting Daily Oracle Scan (Refactored Loop)...")
    
    # --- 3OX AUTOMATIC BACKUP ---
    # create_db_backup()
    # ---------------------------
    
    # --- ARGUMENT PARSING ---
    import argparse
    parser = argparse.ArgumentParser(description="Oracle Scraper Runner")
    parser.add_argument("--shops", nargs="*", help="Specific shops to scrape (e.g. electropolis fantasia)")
    parser.add_argument("--random-delay", type=int, default=0, help="Wait up to X minutes before starting (jitter)")
    parser.add_argument("--deep-harvest", action="store_true", help="Visit individual product pages for EAN/GTIN extraction")
    parser.add_argument("--no-nexus", action="store_true", help="Skip ActionFigure411 Catalog Synchronization")
    args, unknown = parser.parse_known_args()
    
    # --- STAGGERED START (KAIZEN) ---
    if args.random_delay > 0:
        import random
        wait_mins = random.uniform(0, args.random_delay)
        logger.info(f"⏳ Kaizen: Staggered start active. Target wait: {wait_mins:.2f} minutes.")
        
        # Split sleep into smaller chunks for heartbeat logging
        total_wait_secs = int(wait_mins * 60)
        chunk_size = 300 # 5 minutes heartbeat
        slept = 0
        
        while slept < total_wait_secs:
            to_sleep = min(chunk_size, total_wait_secs - slept)
            logger.info(f"😴 Oracle Sleeping... ({slept//60}/{total_wait_secs//60} min elapsed)")
            await asyncio.sleep(to_sleep)
            slept += to_sleep
            
        logger.info("⚡ Oracle Awakening: Delay complete, engaging robots.")
    
    # --- 3OX PID MANAGEMENT ---
    # manage_pid(action="create")
    # --------------------------
        
    try:
        # PHASE 12: Ensure database schema is up to date before scanning
        try:
            from src.infrastructure.universal_migrator import migrate
            logger.info("🔧 Synchronizing database schema (Universal Migrator)...")
            migrate()
        except Exception as e:
            logger.warning(f"⚠️ Migration pre-check failed: {e}")

        # --- PHASE 12.6: NEXO MAESTRO SYNC ---
        if not args.no_nexus:
            try:
                logger.info("📡 Nexus: Engaging Master Catalog Sync...")
                nexus_success = await NexusService.sync_catalog()
                if nexus_success:
                    logger.info("📡 Nexus: Master Catalog is UP TO DATE.")
                else:
                    logger.warning("📡 Nexus: Sync returned failure, proceeding with current catalog...")
            except Exception as e:
                logger.error(f"📡 Nexus: Critical Sync Error: {e}")
        else:
            logger.info("📡 Nexus: Sync skipped by user.")
        # -------------------------------------

        # Initialize Pipeline
        pipeline = ScrapingPipeline([])
        
        # List of Scrapers (Spanish + Phase 8.4 European)
        # REORDER: Spanish first, then International, DeToyboys LAST (User Policy)
        all_scrapers = [
            FantasiaScraper(),
            FrikiversoScraper(),
            FrikimazScraper(),
            PixelatoyScraper(),
            ElectropolisScraper(),
            TriguetechScraper(),
            LaMansionDelTerrorScraper(),
            # European Expansion
            ToymiEUScraper(),
            Time4ActionToysDEScraper(),
            BigBadToyStoreScraper(),
            SmythsToysScraper(),
            AmazonScraper(),
            EbayScraper(),
            VintedScraper(),
            WallapopScraper(), # CON PROBE LOG PROTEGIDO
            # TradeinnScraper(),
            # DeToyboys at the end (User Request)
            DeToyboysNLScraper(),
        ]
        
        # Filter Scrapers
        scrapers = []
        if args.shops:
            target_shops = [s.lower() for s in args.shops if s.strip()]
            if target_shops:
                logger.info(f"🎯 Target Execution: {target_shops}")
                for s in all_scrapers:
                    if s.spider_name.lower() in target_shops or s.shop_name.lower() in target_shops:
                        scrapers.append(s)
            else:
                scrapers = all_scrapers
        else:
            scrapers = all_scrapers
            
        if not scrapers and args.shops:
            logger.warning(f"⚠️ No matching scrapers found for {args.shops}. Running none.")
            scrapers = []
        
        # --- PHASE 42: PURGE OLD LOGS (7 DAYS) ---
        try:
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=7)
            with SessionLocal() as db_purge:
                logger.info("🧹 Purging ancient logs (older than 7 days)...")
                result = db_purge.query(ScraperExecutionLogModel).filter(
                    ScraperExecutionLogModel.start_time < cutoff
                ).delete()
                db_purge.commit()
                logger.info(f"🧹 Purged {result} stale execution records. Systems optimized.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to purge old logs: {e}")
            
        # --- FINOPS DATABASE COMPACTATION & MAINTENANCE ---
        try:
            from src.application.services.maintenance_service import MaintenanceService
            with SessionLocal() as db_maint:
                logger.info("🧹 Iniciando compactación y mantenimiento de base de datos FinOps...")
                stats = MaintenanceService.compact_database(db_maint)
                logger.info(f"🧹 Mantenimiento FinOps completado. Estadísticas: {stats}")
        except Exception as e:
            logger.warning(f"⚠️ Fallo en el mantenimiento de base de datos FinOps: {e}")
        
        results = {}
        total_stats = {"found": 0, "new": 0, "errors": 0}
        failed_spiders = []
        blocked_spiders = []
        start_time = datetime.now()
        
        db = SessionLocal()
        audit = AuditLogger(db)
        notifier = NotifierService()

        total_scrapers = len(scrapers)
        
        # User-Agent List for Rotation
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        import random

        for idx, scraper in enumerate(scrapers):
            try:
                logger.info(f"🕸️ Engaging {scraper.spider_name}...")
                
                # Inject Audit Logger
                scraper.audit_logger = audit

                # UI Progress Update
                progress_val = int((idx / total_scrapers) * 100)
                if progress_callback:
                    progress_callback(scraper.spider_name, progress_val)
                    
                # DB Status Update (Running)
                try:
                    status_row = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == scraper.spider_name).first()
                    if not status_row:
                        status_row = ScraperStatusModel(spider_name=scraper.spider_name)
                        db.add(status_row)
                    status_row.status = "running"
                    status_row.progress = progress_val
                    status_row.last_update = datetime.now()
                    db.commit()
                except Exception:
                    db.rollback()

                # Heartbeat Log
                logger.info(f"💓 Heartbeat: Attempting to engage {scraper.spider_name}...")

                # Determine trigger type (Corrected Phase 50)
                event_name = os.getenv("GITHUB_EVENT_NAME", "manual")
                trigger_type = "scheduled" if event_name == "schedule" else "manual"

                # Log Entry (Running)
                log_entry = ScraperExecutionLogModel(
                    spider_name=scraper.spider_name,
                    status="running",
                    start_time=datetime.now(),
                    trigger_type=trigger_type,
                    logs=""
                )
                try:
                    db.add(log_entry)
                    db.commit()
                    db.refresh(log_entry)
                except Exception:
                    db.rollback()

                def update_task_log(msg: str):
                    logger.info(f"[{scraper.spider_name}] {msg}")
                    try:
                        with SessionLocal() as db_l:
                            l = db_l.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == log_entry.id).first()
                            if l:
                                current = l.logs or ""
                                l.logs = current + f"\n[{datetime.now().strftime('%H:%M:%S')}] {msg}"
                                db_l.commit()
                    except Exception:
                        pass

                scraper.log_callback = update_task_log
                
                try:
                    query = "motu"
                    offers = await scraper.search(query=query)
                    
                    if getattr(scraper, 'blocked', False):
                        logger.warning(f"🛡️ [{scraper.spider_name}] Scraper was marked as BLOCKED by target server.")
                        blocked_spiders.append(scraper.spider_name)
                    elif not offers:
                        logger.info(f"⚪ [{scraper.spider_name}] Scrape completed with 0 items returned.")
                        log_entry.status = "success_empty"
                    
                    # 2. Persist
                    new_items_found = 0
                    if offers:
                        # PHASE 10: Deep Harvest (Precision)
                        if args.deep_harvest and offers:
                            logger.info(f"🔍 [{scraper.spider_name}] Deep Harvest active. Refining {len(offers)} items...")
                            for item in offers:
                                if not getattr(item, 'ean', None):
                                    if hasattr(scraper, '_scrape_detail') and callable(getattr(scraper, '_scrape_detail')):
                                        logger.warning(f"⚠️ Deep harvest for {scraper.spider_name} skipped for {item.product_name} as 'context' is undefined.")
                                    else:
                                        logger.warning(f"⚠️ Scraper {scraper.spider_name} does not implement _scrape_detail for deep harvest.")

                        pipeline.log_callback = update_task_log
                        new_items_found = pipeline.update_database(offers, shop_names=[scraper.shop_name])
                        update_task_log(f"💾 {new_items_found} nuevas reliquias añadidas al Purgatorio.")
                        total_stats["found"] += len(offers)
                        total_stats["new"] += new_items_found
                        
                        # Log Update Success
                        log_entry.items_found = len(offers)
                        log_entry.new_items = new_items_found
                        log_entry.status = "success"
                    else:
                        if getattr(scraper, 'blocked', False):
                            log_entry.status = "blocked"
                        else:
                            log_entry.status = "success_empty"
                    
                    # DB Status Update (Completed)
                    try:
                        if getattr(scraper, 'blocked', False):
                            status_row.status = "blocked"
                        else:
                            status_row.status = "completed"
                        status_row.items_scraped = len(offers) if offers else 0
                        status_row.last_update = datetime.now()
                        
                        # Finalize Log
                        log_entry.end_time = datetime.now()
                        db.commit()
                    except Exception:
                        db.rollback()

                    results[scraper.spider_name] = {"items_found": len(offers), "new_items": new_items_found, "status": "Success"}
                    logger.info(f"✅ [END] {scraper.spider_name} Complete (New: {new_items_found})")
                    update_task_log(f"✅ [FIN] Completado: {len(offers)} encontradas, {new_items_found} nuevas.")
                    
                except Exception as e:
                    logger.error(f"❌ Failed {scraper.spider_name}: {e}")
                    update_task_log(f"❌ ERROR: {str(e)}")
                    results[scraper.spider_name] = {"error": str(e)}
                    total_stats["errors"] += 1
                    failed_spiders.append(f"{scraper.spider_name} ({str(e)[:60]})")
                    
                    # DB Status Update (Error)
                    try:
                        status_row.status = "error"
                        log_entry.status = "error"
                        log_entry.error_message = str(e)[:500]
                        log_entry.end_time = datetime.now()
                        db.commit()
                    except Exception:
                        db.rollback()
            except Exception as crash:
                logger.critical(f"🔥 Catastrophic Scraper Crash ({scraper.spider_name}): {crash}")
                total_stats["errors"] += 1
                failed_spiders.append(f"{scraper.spider_name} ({str(crash)[:60]})")
            
        # Final Callback
        if progress_callback:
            progress_callback("Completado", 100)
        
        db.close()

        # PHASE 18: Create Database Vault (Safe Backup)
        try:
            from src.core.backup_manager import BackupManager
            logger.info("🏰 Sealing the Data Vault (Database Backup)...")
            backup_db = SessionLocal()
            bm = BackupManager()
            backup_path = bm.create_database_backup(backup_db)
            if backup_path:
                logger.info(f"🛡️ Vault sealed at: {backup_path}")
            backup_db.close()
        except Exception as e_bk:
            logger.warning(f"⚠️ Error durante el sellado del vault de backup: {e_bk}")

        # PHASE 88: Auto-resolución de Lore para productos nuevos (Caché permanente, 0 coste de red)
        try:
            from src.application.services.lore_harvester_service import LoreHarvesterService
            with SessionLocal() as db_lore:
                unlinked = db_lore.query(ProductModel).filter(ProductModel.character_slug == None).all()
                if unlinked:
                    logger.info(f"🔮 Auto-resolviendo lore para {len(unlinked)} productos sin vincular...")
                    for p in unlinked:
                        lore = LoreHarvesterService.get_or_create_character_lore(db_lore, p.name)
                        p.character_slug = lore.slug
                    db_lore.commit()
                    logger.info("✨ Auto-resolución de lore finalizada.")
        except Exception as e_lore:
            logger.warning(f"⚠️ Error en la auto-asignación de lore durante Daily Scan: {e_lore}")

        duration = datetime.now() - start_time
        logger.info(f"🏁 Daily Scan Complete in {duration}. Total: {total_stats}")
        
        # Notificación final por Telegram al administrador
        try:
            from src.core.security import SecurityShield
            from src.domain.models import PendingMatchModel
            
            with SessionLocal() as db_purg:
                purg_count = db_purg.query(PendingMatchModel).filter(
                    PendingMatchModel.first_seen_at >= start_time
                ).count()
                
                error_section = ""
                if failed_spiders:
                    failed_list = "\n".join([f"  • ⚠️ <code>{f}</code>" for f in failed_spiders[:5]])
                    error_section = f"\n\n<b>Incidencias en Scrapers ({len(failed_spiders)}):</b>\n{failed_list}"
                
                blocked_section = ""
                if blocked_spiders:
                    blocked_list = ", ".join(blocked_spiders)
                    blocked_section = f"\n🛡️ <i>Tiendas bloqueadas: {blocked_list}</i>"

                tg_msg = (
                    "🏁 <b>Daily Scan Completado</b>\n\n"
                    f"⏱️ Duración: <b>{str(duration).split('.')[0]}</b>\n"
                    f"🔍 Ofertas Procesadas: <b>{total_stats['found']}</b>\n"
                    f"🆕 Nuevas Ofertas Inyectadas: <b>{total_stats['new']}</b>\n"
                    f"⚖️ Enviados al Purgatorio: <b>{purg_count}</b>\n"
                    f"❌ Errores en Scrapers: <b>{total_stats['errors']}</b>"
                    f"{error_section}"
                    f"{blocked_section}\n\n"
                    "🛡️ <i>¡El Oráculo de Nueva Eternia sigue vigilando!</i>"
                )
                await SecurityShield.send_telegram_alert(tg_msg)
                logger.info("📡 Reporte final del Daily Scan enviado a Telegram.")
        except Exception as tg_ex:
            logger.error(f"⚠️ No se pudo enviar el reporte del Daily Scan a Telegram: {tg_ex}")

        # Registrar resumen global de ejecución en base de datos para métricas de cuota
        try:
            with SessionLocal() as db_summary:
                event_name = os.getenv("GITHUB_EVENT_NAME", "manual")
                trigger = "scheduled" if event_name == "schedule" else "manual"
                db_summary.add(ScraperExecutionLogModel(
                    spider_name="DailyScan",
                    status="success" if total_stats["errors"] == 0 else "error",
                    items_found=total_stats["found"],
                    new_items=total_stats["new"],
                    errors=total_stats["errors"],
                    start_time=start_time,
                    end_time=datetime.now(),
                    trigger_type=trigger,
                    logs=f"Daily Scan completo finalizado en {str(duration).split('.')[0]}. Ofertas: {total_stats['found']}, Nuevas: {total_stats['new']}, Errores: {total_stats['errors']}."
                ))
                db_summary.commit()
        except Exception as sum_ex:
            logger.error(f"⚠️ Error guardando log global de DailyScan: {sum_ex}")
            
    except Exception as fatal_e:
        logger.critical(f"🔥 Error fatal en run_daily_scan: {fatal_e}")
        try:
            from src.core.security import SecurityShield
            err_alert = (
                "🚨 <b>[Daily Scan: FALLO CRÍTICO]</b>\n\n"
                f"❌ <b>Motivo:</b> <code>{type(fatal_e).__name__}: {str(fatal_e)[:300]}</code>\n"
                f"⏱️ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                "🛡️ <i>El Oráculo ha registrado el incidente. Se requiere revisión.</i>"
            )
            await SecurityShield.send_telegram_alert(err_alert)
        except Exception as tg_err:
            logger.error(f"No se pudo enviar la alerta de fallo crítico a Telegram: {tg_err}")
        raise fatal_e

if __name__ == "__main__":
    try:
        asyncio.run(run_daily_scan())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # --- EMERGENCY DB LOGGING ---
        try:
            db_err = SessionLocal()
            log_err = ScraperExecutionLogModel(
                spider_name="Global_System",
                status="critical_failure",
                start_time=datetime.now(),
                end_time=datetime.now(),
                trigger_type="scheduled",
                error_message=f"CRITICAL SCRIPT FAILURE: {str(e)}\n\n{traceback.format_exc()}"[:2000]
            )
            db_err.add(log_err)
            db_err.commit()
            db_err.close()
            print(">> CRITICAL ERROR LOGGED TO DB")
        except Exception as db_ex:
            print(f">> FAILED TO LOG TO DB: {db_ex}")
        # ----------------------------
        
        # input("Press Enter to exit (Debug Mode)...")
