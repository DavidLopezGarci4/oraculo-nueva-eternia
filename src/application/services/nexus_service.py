import os
import logging
from src.infrastructure.collectors.personal_collection import main as run_scraper
from scripts.phase0_migration import migrate_excel_to_db
from src.infrastructure.database_cloud import SessionCloud
from src.core.config import settings

logger = logging.getLogger("NexusService")

class NexusService:
    @staticmethod
    async def sync_catalog():
        """
        Orchestrates the full catalog sync:
        1. Run personal_collection.py (Web -> Excel & Images)
        2. Run phase0_migration.py (Excel -> DB)
        """
        logger.info("📡 Nexus: Starting Catalog Synchronization...")
        
        try:
            # 1. Scrape Web to Excel
            logger.info("📡 Nexus Step 1: Capturing ActionFigure411 data...")
            run_scraper()
            
            # 2. Migrate Excel to DB
            logger.info("📡 Nexus Step 2: Injecting data into Oracle DB...")
            db = SessionCloud()
            
            # Resolve paths relative to project root safely (Phase 35 Structure)
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            excel_path = project_root / "data" / "MOTU" / "lista_MOTU.xlsx"
            
            if not excel_path.exists():
                logger.error(f"❌ Nexus Error: Catalog Excel not found at {excel_path}")
                return False
            
            migrate_excel_to_db(str(excel_path), db)
            
            # 3. Cloud Image Synchronization (Supabase Storage)
            logger.info("📡 Nexus Step 3: Synchronizing images to Cloud (Supabase)...")
            try:
                from src.application.services.storage_service import StorageService
                storage = StorageService()
                await storage.ensure_bucket()
                
                images_dir = os.path.join(os.path.dirname(str(excel_path)), "images")
                storage.upload_all_local_images(images_dir)
                
            except Exception as se:
                logger.error(f"⚠️ Image Sync Warning: {se}")

            db.close()
            
            logger.info("📡 Nexus: Catalog and Images synchronized successfully (DB Updated during Step 2).")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Nexus Error: {e}")
            logger.error(traceback.format_exc())
            return False
