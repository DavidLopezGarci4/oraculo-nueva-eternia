import os
import logging
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from src.infrastructure.collectors.personal_vintage_collection import main as run_scraper
from scripts.phase0_vintage_migration import migrate_excel_to_db
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel
from src.core.config import settings

logger = logging.getLogger("NexusVintageService")

class TelemetryHandler(logging.Handler):
    """Logging handler that pipes logs to the ScraperExecutionLogModel in DB."""
    def __init__(self, log_id: int):
        super().__init__()
        self.log_id = log_id
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record):
        try:
            msg = self.format(record)
            ts = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%H:%M:%S")
            line = f"[{ts}] {msg}"
            
            with SessionCloud() as db:
                db.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == self.log_id).update({
                    "logs": ScraperExecutionLogModel.logs + "\n" + line
                })
                db.commit()
        except Exception:
            pass

class NexusVintageService:
    @staticmethod
    def purge_catalog(db, safe_mode: bool = True):
        """
        Wipes Vintage products and links. 
        If safe_mode=True (default), user collection items are PRESERVED.
        If safe_mode=False, wipes everything vintage.
        """
        from src.domain.models import ProductModel, CollectionItemModel, OfferModel, ProductAliasModel, PriceHistoryModel
        
        logger.warning(f"🛡️ Vintage Guardian: PURGE (SafeMode={safe_mode}) - Processing Vintage segregation.")
        
        vintage_products = db.query(ProductModel).filter(ProductModel.is_vintage == True).all()
        vintage_ids = [p.id for p in vintage_products]
        
        if not vintage_ids:
            logger.info("ℹ️ Purge: No existing vintage products found.")
            return

        db.query(PriceHistoryModel).filter(PriceHistoryModel.offer_id.in_(
            db.query(OfferModel.id).filter(OfferModel.product_id.in_(vintage_ids))
        )).delete(synchronize_session=False)
        
        db.query(OfferModel).filter(OfferModel.product_id.in_(vintage_ids)).delete(synchronize_session=False)
        
        if not safe_mode:
            db.query(CollectionItemModel).filter(CollectionItemModel.product_id.in_(vintage_ids)).delete(synchronize_session=False)
            
        db.query(ProductAliasModel).filter(ProductAliasModel.product_id.in_(vintage_ids)).delete(synchronize_session=False)
        db.query(ProductModel).filter(ProductModel.id.in_(vintage_ids)).delete(synchronize_session=False)
        db.commit()
        logger.info(f"☢️ VINTAGE PURGE: Database is now clean of vintage items (SafeMode={safe_mode}).")

    @staticmethod
    async def sync_catalog(purge_before_sync: bool = False):
        """
        Orchestrates the full vintage catalog sync with detailed telemetry.
        """
        # Ensure DB schema is ready
        try:
            from src.infrastructure.universal_migrator import migrate
            logger.info("📡 Paso 0 (Infraestructura): Sincronizando esquema de base de datos...")
            migrate()
        except Exception as me:
            logger.error(f"❌ Error Crítico de Infraestructura: {me}")
        
        # Initialize Telemetry entry
        with SessionCloud() as db:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "NexusVintage").first()
            if not status:
                status = ScraperStatusModel(spider_name="NexusVintage", status="stopped")
                db.add(status)
            
            status.status = "running"
            status.start_time = datetime.utcnow()
            
            exec_log = ScraperExecutionLogModel(
                spider_name="NexusVintage",
                status="running",
                start_time=status.start_time,
                trigger_type="manual",
                logs=f"[{datetime.now(ZoneInfo('Europe/Madrid')).strftime('%H:%M:%S')}] 🚀 Iniciando Sincronización del Nexo Maestro Vintage...\n"
            )
            db.add(exec_log)
            db.commit()
            log_id = exec_log.id

        # Attach telemetry handler
        telemetry_handler = TelemetryHandler(log_id)
        telemetry_handler.setLevel(logging.INFO)
        root_logger = logging.getLogger()
        root_logger.addHandler(telemetry_handler)
        
        logger.info("📡 Inicio: Preparando motores de migración Vintage...")
        
        try:
            loop = asyncio.get_event_loop()
            
            if purge_before_sync:
                logger.warning("📡 Paso 0.5: Purgando catálogo Vintage existente...")
                with SessionCloud() as db_purge:
                    NexusVintageService.purge_catalog(db_purge, safe_mode=True)
            
            # Backup collection stock using GuardianService before any change
            from src.application.services.guardian_service import GuardianService
            with SessionCloud() as db_guard:
                GuardianService.backup_stock(db_guard)

            # 1. Scrape Web to Excel
            logger.info("📡 Paso 1: Capturando datos de ActionFigure411 Vintage (Raspado Web)...")
            await loop.run_in_executor(None, run_scraper)
            
            # 2. Migrate Excel to DB
            logger.info("📡 Paso 2: Inyectando datos Vintage en la Base de Datos...")
            
            def run_migration_task():
                db_mig = SessionCloud()
                try:
                    project_root = Path(__file__).resolve().parent.parent.parent.parent
                    excel_path = project_root / "data" / "MOTU" / "lista_vintage.xlsx"
                    
                    if not excel_path.exists():
                        raise FileNotFoundError(f"Archivo Excel Vintage no encontrado en {excel_path}")
                    
                    migrate_excel_to_db(str(excel_path), db_mig)
                    return excel_path
                finally:
                    db_mig.close()

            excel_path = await loop.run_in_executor(None, run_migration_task)
            
            # 3. Cloud Image Synchronization (Supabase Storage in /vintage/ subfolder)
            logger.info("📡 Paso 3: Sincronizando imágenes Vintage con la Nube (Supabase)...")
            try:
                from src.application.services.storage_service import StorageService
                storage = StorageService()
                bucket_ok = await storage.ensure_bucket()
                
                if bucket_ok:
                    images_dir = os.path.join(os.path.dirname(str(excel_path)), "vintage_images")
                    # Upload all images into the specific "vintage" subfolder inside the bucket
                    await loop.run_in_executor(None, storage.upload_all_local_images, images_dir, "vintage")
                else:
                    logger.warning("⚠️ Cloud storage sync bypassed (Supabase Storage is unavailable or locked). Local files are fully functional.")
            except Exception as se:
                logger.warning(f"⚠️ Aviso en Sincro de Imágenes Vintage: {se}")

            logger.info("✅ Nexus Vintage: Catálogo e imágenes sincronizados con éxito.")
            
            # Finalize Status
            with SessionCloud() as db:
                db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "NexusVintage").update({
                    "status": "completed",
                    "end_time": datetime.utcnow()
                })
                db.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == log_id).update({
                    "status": "success",
                    "end_time": datetime.utcnow()
                })
                db.commit()
                
            return True
            
        except Exception as e:
            error_detail = f"{str(e)}"
            logger.error(f"❌ Error en Nexus Vintage: {error_detail}")
            
            with SessionCloud() as db:
                db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "NexusVintage").update({
                    "status": "error",
                    "end_time": datetime.utcnow()
                })
                db.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == log_id).update({
                    "status": "error",
                    "error_message": error_detail,
                    "end_time": datetime.utcnow()
                })
                db.commit()
            return False
        finally:
            root_logger.removeHandler(telemetry_handler)
