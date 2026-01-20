import os
import logging
from pathlib import Path
from supabase import create_client, Client
from src.core.config import settings

logger = logging.getLogger("StorageService")

class StorageService:
    def __init__(self):
        url: str = settings.SUPABASE_URL
        key: str = settings.SUPABASE_SERVICE_ROLE_KEY # Requires service role for uploads
        if not url or not key:
            logger.error("❌ Supabase credentials missing (URL or Service Role Key)")
            self.client = None
        else:
            self.client: Client = create_client(url, key)
        
        self.bucket_name = "motu-catalog"

    async def ensure_bucket(self):
        """Ensures the motu-catalog bucket exists and is public."""
        if not self.client: return False
        try:
            # Check if bucket exists
            buckets = self.client.storage.list_buckets()
            if not any(b.name == self.bucket_name for b in buckets):
                logger.info(f" Creating bucket: {self.bucket_name}")
                self.client.storage.create_bucket(self.bucket_name, options={"public": True})
            return True
        except Exception as e:
            logger.error(f"❌ Error ensuring bucket: {e}")
            return False

    def upload_image(self, local_path: str) -> str:
        """
        Uploads a local image to Supabase Storage.
        Returns the public URL of the uploaded image.
        """
        if not self.client: 
             logger.warning("⚠️ Storage client not initialized. Skipping upload.")
             return None
             
        path = Path(local_path)
        if not path.exists():
            logger.warning(f"⚠️ Local image not found: {local_path}")
            return None

        file_name = path.name
        
        try:
            # Upload file
            with open(local_path, "rb") as f:
                # We overwrite if exists to ensure latest version
                self.client.storage.from_(self.bucket_name).upload(
                    file_name, 
                    f, 
                    file_options={"upsert": "true", "content-type": "image/jpeg"}
                )
            
            # Get Public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_name)
            logger.info(f"✅ Image uploaded: {file_name} -> {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Error uploading {file_name}: {e}")
            return None

    def upload_all_local_images(self, images_dir: str):
         """Syncs all images in the local folder to the cloud."""
         logger.info(f"🔄 Syncing all images from {images_dir} to Cloud...")
         p = Path(images_dir)
         if not p.exists(): return
         
         count = 0
         for img_file in p.glob("*.jpg"):
             url = self.upload_image(str(img_file))
             if url: count += 1
         
         logger.info(f"✅ Sync complete: {count} images pushed to Supabase.")
