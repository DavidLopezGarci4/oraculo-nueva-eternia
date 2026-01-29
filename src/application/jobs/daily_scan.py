import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from vec3.dev.adapters import initialize_runtime, create_db_backup, manage_pid, check_stop_signal, save_json_report

# Initialize 3OX Runtime (Force UTF-8, Path Resolution)
root_path = initialize_runtime()

from src.core.logger import setup_logging
from loguru import logger
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
# ... (rest of imports)

# New Refactored Scrapers
from src.infrastructure.scrapers.action_toys_scraper import ActionToysScraper
from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
from src.infrastructure.scrapers.frikiverso_scraper import FrikiversoScraper
from src.infrastructure.scrapers.pixelatoy_scraper import PixelatoyScraper
from src.infrastructure.scrapers.electropolis_scraper import ElectropolisScraper

# Phase 8.4: European Expansion Scrapers
from src.infrastructure.scrapers.detoyboys_scraper import DeToyboysNLScraper

# Phase 8.4b: Advanced Expansion Scrapers
from src.infrastructure.scrapers.toymi_scraper import ToymiEUScraper
from src.infrastructure.scrapers.time4actiontoys_scraper import Time4ActionToysDEScraper
from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.infrastructure.scrapers.ebay_scraper import EbayScraper
from src.application.services.nexus_service import NexusService

# Domain & Infra Models
from src.infrastructure.database_cloud import SessionCloud as SessionLocal # Unified for Cloud
from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel, ProductModel, CollectionItemModel, LogisticRuleModel
from src.core.audit_logger import AuditLogger
from src.core.notifier import NotifierService
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService

async def run_daily_scan(progress_callback=None):
    # Ensure logging is set up
    # setup_logging() # Already called at module level or by importer
    logger.info("🚀 Starting Daily Oracle Scan (Refactored Loop)...")
    
    # --- 3OX AUTOMATIC BACKUP ---
    create_db_backup()
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
    manage_pid(action="create")
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
            ActionToysScraper(),
            FantasiaScraper(),
            FrikiversoScraper(),
            PixelatoyScraper(),
            ElectropolisScraper(),
            # European Expansion
            ToymiEUScraper(),
            Time4ActionToysDEScraper(),
            BigBadToyStoreScraper(),
            AmazonScraper(),
            EbayScraper(),
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
                    if any(t in s.spider_name.lower() for t in target_shops):
                        scrapers.append(s)
            else:
                scrapers = all_scrapers
        else:
            scrapers = all_scrapers
            
    except Exception as e:
        logger.error(f"Failed to initialize scrapers: {e}")
        scrapers = []
    
    # --- PHASE 42: PURGE OLD LOGS (7 DAYS) ---
    try:
        from sqlalchemy import text
        with SessionLocal() as db_purge:
            logger.info("🧹 Purging ancient logs (older than 7 days)...")
            result = db_purge.execute(text(
                "DELETE FROM scraper_execution_logs WHERE start_time < datetime('now', '-7 days')"
            ))
            db_purge.commit()
            logger.info(f"🧹 Purged {result.rowcount} stale execution records. Systems optimized.")
    except Exception as e:
        logger.warning(f"⚠️ Failed to purge old logs: {e}")
    
    results = {}
    total_stats = {"found": 0, "new": 0, "errors": 0}
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
            # Check for 3OX Stop Signal
            if check_stop_signal():
                break
                
            logger.info(f"🕸️ Engaging {scraper.spider_name}...")
            
            # Scrapers now manage their own stealth contexts for maximum robustness
            
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

            # Create Execution Log Entry
            log_entry = ScraperExecutionLogModel(
                spider_name=scraper.spider_name,
                status="running",
                start_time=datetime.now(),
                trigger_type="manual" if args.shops else "scheduled",
                logs=f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Inicia incursion en {scraper.spider_name}\n"
            )
            try:
                db.add(log_entry)
                db.commit()
                log_id = log_entry.id
            except Exception as e:
                logger.error(f"Failed to create execution log: {e}")
                db.rollback()
                log_id = None

            # Helper to append logs to DB entry safely
            def update_task_log(msg):
                if not log_id: return
                try:
                    # New session to avoid interferences with the main loop
                    with SessionLocal() as db_log:
                        entry = db_log.query(ScraperExecutionLogModel).get(log_id)
                        if entry:
                            ts = datetime.now().strftime("%H:%M:%S")
                            new_line = f"[{ts}] {msg}"
                            if entry.logs: entry.logs += "\n" + new_line
                            else: entry.logs = new_line
                            db_log.commit()
                except Exception as ex:
                    logger.warning(f"Log preservation failed: {ex}")

            update_task_log(f"🕸️ Engaging {scraper.spider_name}...")

            try: # Robustness Layer: Ensure loop continues even if a scraper crashes
                try: # Main try block for scraping and persistence
                    # 1. Scrape (Modern scrapers use .search)
                    logger.info(f"🛡️  [START] Incursion {scraper.spider_name} initiated...")
                    update_task_log(f"🛡️  [START] Incursion {scraper.spider_name} initiated...")
                    # Set 10-minute timeout per scraper for Cloud stability
                    try:
                        offers = await asyncio.wait_for(scraper.search("auto"), timeout=600)
                        update_task_log(f"📡 Found {len(offers)} potential relics.")
                    except asyncio.TimeoutError:
                        logger.error(f"⌛ [TIMEOUT] {scraper.spider_name} exceeded 10-minute limit. Forcefully aborting this spider.")
                        update_task_log("⌛ [TIMEOUT] Exceeded 10-minute limit. Aborting.")
                        offers = []
                    
                    # PHASE 19: Health & Block Alerts (Sentinel)
                    if not offers:
                        if getattr(scraper, 'blocked', False):
                            logger.error(f"[{scraper.spider_name}] 🚫 Blocked by anti-bot measures.")
                            msg = f"🚫 **DESTIERRO DETECTADO**\n\nEl Oráculo ha sido bloqueado por **{scraper.spider_name}**. Se requieren medidas de evasión táctica."
                            await notifier.send_message(msg)
                            log_entry.status = "blocked"
                            log_entry.error_message = "Anti-bot block detected"
                        else:
                            logger.warning(f"[{scraper.spider_name}] ⚠️ Empty scan results.")
                            # Alert if this is a shop that usually has items (most of them)
                            msg = f"⚠️ **SALUD COMPROMETIDA**\n\nEl scraper de **{scraper.spider_name}** ha devuelto 0 resultados. Podría ser un cambio de estructura HTML o falta de stock real."
                            await notifier.send_message(msg)
                            log_entry.status = "empty_warning"
                    
                    # 2. Persist
                    if offers:
                        # PHASE 10: Deep Harvest (Precision)
                        if args.deep_harvest and offers:
                            logger.info(f"🔍 [{scraper.spider_name}] Deep Harvest active. Refining {len(offers)} items...")
                            for item in offers:
                                # Visit detail page if EAN is missing and we want precision
                                if not getattr(item, 'ean', None):
                                    # Ensure the scraper has a _scrape_detail method
                                    if hasattr(scraper, '_scrape_detail') and callable(getattr(scraper, '_scrape_detail')):
                                        logger.warning(f"⚠️ Deep harvest for {scraper.spider_name} skipped for {item.product_name} as 'context' is undefined.")
                                    else:
                                        logger.warning(f"⚠️ Scraper {scraper.spider_name} does not implement _scrape_detail for deep harvest.")

                        # Update Database
                        pipeline.update_database(offers)
                        update_task_log("💾 Relics persisted in the Great Library.")
                        stats = {
                            "items_found": len(offers),
                            "status": "Success"
                        }
                        total_stats["found"] += len(offers)
                        
                        # Log Update Success
                        log_entry.items_found = len(offers)
                        log_entry.status = "success"
                    else:
                        stats = {"items_found": 0, "status": "Empty"}
                        log_entry.status = "success_empty"
                    
                    # DB Status Update (Completed)
                    try:
                        status_row.status = "completed"
                        status_row.items_scraped = len(offers) if offers else 0
                        status_row.last_update = datetime.now()
                        
                        # Finalize Log
                        log_entry.end_time = datetime.now()
                        db.commit()
                    except Exception:
                        db.rollback()

                    results[scraper.spider_name] = stats
                    logger.info(f"✅ [END] {scraper.spider_name} Complete: {stats}")
                    update_task_log(f"✅ [END] Complete: {stats['items_found']} found.")
                    
                except Exception as e:
                    logger.error(f"❌ Failed {scraper.spider_name}: {e}")
                    update_task_log(f"❌ ERROR: {str(e)}")
                    results[scraper.spider_name] = {"error": str(e)}
                    total_stats["errors"] += 1
                    
                    # DB Status Update (Error)
                    try:
                        status_row.status = "error"
                        
                        # Finalize Log Error
                        log_entry.status = "error"
                        log_entry.error_message = str(e)[:500]
                        log_entry.end_time = datetime.now()
                        
                        db.commit()
                    except Exception:
                        db.rollback()
            except Exception as crash:
                logger.critical(f"🔥 Catastrophic Scraper Crash ({scraper.spider_name}): {crash}")
                total_stats["errors"] += 1
        
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
    except Exception as e:
        logger.error(f"⚠️ Failed to seal Data Vault: {e}")

    duration = datetime.now() - start_time
    logger.info(f"🏁 Daily Scan Complete in {duration}. Total: {total_stats}")
    
    # 3OX Reporting
    save_json_report(results, filename_prefix="daily_scan")
        
    # 3OX PID Cleanup
    manage_pid(action="remove")

if __name__ == "__main__":
    try:
        # if sys.platform == "win32":
        #    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(run_daily_scan())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # --- EMERGENCY DB LOGGING ---
        try:
            db_err = SessionLocal()
            log_err = ScraperExecutionLogModel(
                spider_name="Global_System", # Special name for script-wide errors
                status="critical_failure",
                start_time=datetime.now(),
                end_time=datetime.now(),
                trigger_type="scheduled", # Assume scheduled if crashing
                error_message=f"CRITICAL SCRIPT FAILURE: {str(e)}\n\n{traceback.format_exc()}"[:2000] # Truncate for safety
            )
            db_err.add(log_err)
            db_err.commit()
            db_err.close()
            print(">> CRITICAL ERROR LOGGED TO DB")
        except Exception as db_ex:
            print(f">> FAILED TO LOG TO DB: {db_ex}")
        # ----------------------------
        
        # input("Press Enter to exit (Debug Mode)...")
