import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from src.infrastructure.collectors.personal_collection import main as run_scraper
from scripts.phase0_migration import migrate_excel_to_db
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel
from src.core.config import settings

logger = logging.getLogger("NexusService")

class TelemetryHandler(logging.Handler):
    """Logging handler that pipes logs to the ScraperExecutionLogModel in DB."""
    def __init__(self, log_id: int):
        super().__init__()
        self.log_id = log_id
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record):
        try:
            msg = self.format(record)
            ts = datetime.utcnow().strftime("%H:%M:%S")
            line = f"[{ts}] {msg}"
            
            with SessionCloud() as db:
                db.query(ScraperExecutionLogModel).filter(ScraperExecutionLogModel.id == self.log_id).update({
                    "logs": ScraperExecutionLogModel.logs + "\n" + line
                })
                db.commit()
        except Exception:
            pass # Avoid infinite loops or crashing the app due to logging errors

class NexusService:
    @staticmethod
    def purge_catalog(db, safe_mode: bool = True):
        """
        Wipes products and links. 
        If safe_mode=True (default), user collection items are PRESERVED.
        If safe_mode=False, a pre-flight backup is created before wiping everything.
        """
        from src.domain.models import ProductModel, CollectionItemModel, OfferModel, ProductAliasModel, PriceHistoryModel
        from src.application.services.guardian_service import GuardianService
        
        if safe_mode:
            logger.warning("🛡️ Guardian: PURGE (SAFE MODE) - Preserving user collection items.")
        else:
            logger.warning("☢️ Guardian: PURGE (FORCE) - Wiping EVERYTHING including collection.")
            # FORCE BACKUP before nuclear wipe
            GuardianService.backup_stock(db)

        # Order matters for foreign keys: Price History references Offers
        db.query(PriceHistoryModel).delete()
        db.query(OfferModel).delete()
        
        if not safe_mode:
            db.query(CollectionItemModel).delete()
            
        db.query(ProductAliasModel).delete()
        db.query(ProductModel).delete()
        db.commit()
        logger.info(f"☢️ PURGE: Database is now clean (SafeMode={safe_mode}).")

    @staticmethod
    async def sync_catalog(purge_before_sync: bool = False):
        """
        Orchestrates the full catalog sync with detailed telemetry.
        """
        # 0. Infrastructure Guard: Ensure DB Schema is ready BEFORE any queries
        try:
            from src.infrastructure.universal_migrator import migrate
            # Use a new event loop or run in executor if needed, but migrate() is sync
            logger.info("📡 Paso 0 (Infraestructura): Sincronizando esquema de base de datos...")
            migrate()
        except Exception as me:
            logger.error(f"❌ Error Crítico de Infraestructura: {me}")
            # Even if it fails, we try to proceed to see if tables exist
        
        # Initialize Telemetry entry (Now safe because migrate() ran)
        with SessionCloud() as db:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "Nexus").first()
            if not status:
                status = ScraperStatusModel(spider_name="Nexus", status="stopped")
                db.add(status)
            
            status.status = "running"
            status.start_time = datetime.utcnow()
            
            exec_log = ScraperExecutionLogModel(
                spider_name="Nexus",
                status="running",
                start_time=status.start_time,
                trigger_type="manual",
                logs=f"[{datetime.utcnow().strftime('%H:%M:%S')}] 🚀 Iniciando Sincronización del Nexo Maestro...\n"
            )
            db.add(exec_log)
            db.commit()
            log_id = exec_log.id

        # Attach telemetry handler to capture all INFO logs from sub-modules
        telemetry_handler = TelemetryHandler(log_id)
        telemetry_handler.setLevel(logging.INFO)
        root_logger = logging.getLogger()
        root_logger.addHandler(telemetry_handler)
        
        logger.info("📡 Inicio: Preparando motores de migración...")
        
        try:
            loop = asyncio.get_event_loop()
            
            if purge_before_sync:
                logger.warning("📡 Paso 0.5: Purgando catálogo existente por petición del usuario...")
                with SessionCloud() as db_purge:
                    # Guardian Safety is now default here
                    NexusService.purge_catalog(db_purge, safe_mode=True)
            
            # 🛡️ ALWAYS backup stock before any sync, just in case
            from src.application.services.guardian_service import GuardianService
            with SessionCloud() as db_guard:
                GuardianService.backup_stock(db_guard)

            # 1. Scrape Web to Excel
            logger.info("📡 Paso 1: Capturando datos de ActionFigure411 (Raspado Web)...")
            await loop.run_in_executor(None, run_scraper)
            
            # 2. Migrate Excel to DB
            logger.info("📡 Paso 2: Inyectando datos en la Base de Datos Oracle...")
            
            def run_migration_task():
                db_mig = SessionCloud()
                try:
                    project_root = Path(__file__).resolve().parent.parent.parent.parent
                    excel_path = project_root / "data" / "MOTU" / "lista_MOTU.xlsx"
                    
                    if not excel_path.exists():
                        raise FileNotFoundError(f"Archivo Excel no encontrado en {excel_path}")
                    
                    migrate_excel_to_db(str(excel_path), db_mig)
                    return excel_path
                finally:
                    db_mig.close()

            excel_path = await loop.run_in_executor(None, run_migration_task)
            
            # 3. Cloud Image Synchronization (Supabase Storage)
            logger.info("📡 Paso 3: Sincronizando imágenes con la Nube (Supabase)...")
            try:
                from src.application.services.storage_service import StorageService
                storage = StorageService()
                await storage.ensure_bucket()
                
                images_dir = os.path.join(os.path.dirname(str(excel_path)), "images")
                await loop.run_in_executor(None, storage.upload_all_local_images, images_dir)
            except Exception as se:
                logger.warning(f"⚠️ Aviso en Sincro de Imágenes: {se}")

            logger.info("✅ Nexus: Catálogo e imágenes sincronizados con éxito.")
            
            # Finalize Status
            with SessionCloud() as db:
                db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "Nexus").update({
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
            logger.error(f"❌ Error en Nexus: {error_detail}")
            
            with SessionCloud() as db:
                db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == "Nexus").update({
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
            # Always remove handler to avoid leaking memory/handlers
            root_logger.removeHandler(telemetry_handler)
