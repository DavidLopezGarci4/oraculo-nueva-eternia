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
            
            # Fix: Calculate BASE_DIR if missing from settings
            base_dir = getattr(settings, "BASE_DIR", os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            excel_path = os.path.join(base_dir, "src", "data", "MOTU", "lista_MOTU.xlsx")
            
            if not os.path.exists(excel_path):
                # Fallback to absolute path provided by USER environment
                excel_path = "c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia/src/data/MOTU/lista_MOTU.xlsx"
            
            migrate_excel_to_db(excel_path, db)
            
            # 3. Cloud Image Synchronization (Supabase Storage)
            logger.info("📡 Nexus Step 3: Synchronizing images to Cloud (Supabase)...")
            try:
                from src.application.services.storage_service import StorageService
                storage = StorageService()
                await storage.ensure_bucket()
                
                images_dir = os.path.join(os.path.dirname(excel_path), "images")
                storage.upload_all_local_images(images_dir)
                
                # 4. Update Database with Cloud URLs (Post-processing)
                logger.info("📡 Nexus Step 4: Updating database with public URLs...")
                from src.domain.models import ProductModel
                products = db.query(ProductModel).all()
                count = 0
                for p in products:
                    # If we have a local record of the image, we ensure the cloud URL is set
                    # The storage logic uses the filename as the key.
                    # We assume path convention matches our scraper: images/[filename].jpg
                    if p.figure_id:
                        # Find potential filename in images dir
                        from pathlib import Path
                        filename = f"image_{p.figure_id}.jpg" # Common pattern
                        # We try to see if it exists in storage (or just update the URL if we trust the sync)
                        public_url = storage.client.storage.from_(storage.bucket_name).get_public_url(filename)
                        
                        if public_url and p.image_url != public_url:
                            p.image_url = public_url
                            count += 1
                
                db.commit()
                logger.info(f"✅ Database updated: {count} products now pointing to Supabase Cloud.")
                
            except Exception as se:
                logger.error(f"⚠️ Image Sync Warning: {se}")

            db.close()
            
            logger.info("📡 Nexus: Catalog and Images synchronized successfully.")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Nexus Error: {e}")
            logger.error(traceback.format_exc())
            return False
