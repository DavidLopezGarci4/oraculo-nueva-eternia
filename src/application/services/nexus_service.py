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
            excel_path = os.path.join(settings.BASE_DIR, "data", "MOTU", "lista_MOTU.xlsx")
            
            if not os.path.exists(excel_path):
                # Try fallback path
                excel_path = "c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia/data/MOTU/lista_MOTU.xlsx"
            
            migrate_excel_to_db(excel_path, db)
            db.close()
            
            logger.info("📡 Nexus: Catalog synchronized successfully.")
            return True
            
        except Exception as e:
            logger.error(f"❌ Nexus Error: {e}")
            return False
