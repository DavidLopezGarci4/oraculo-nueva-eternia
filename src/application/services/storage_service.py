import asyncio
import os
import logging
from pathlib import Path
from typing import Any, Dict
from src.core.config import settings
from src.core.image_utils import encode_webp_file, has_webp_magic

logger = logging.getLogger("StorageService")

# Module-level symbol preserved for deterministic test patching; real SDK imported lazily in __init__.
create_client = None
Client = Any


class StorageService:
    def __init__(self):
        url: str = settings.SUPABASE_URL
        key: str = settings.SUPABASE_SERVICE_ROLE_KEY # Requires service role for uploads
        if not url or not key:
            logger.error("❌ Supabase credentials missing (URL or Service Role Key)")
            self.client = None
        else:
            factory = create_client
            if factory is None:
                from supabase import create_client as _supabase_create_client
                factory = _supabase_create_client
            self.client: Any = factory(url, key)
        
        self.bucket_name = "motu-catalog"
        self.storage_disabled = False

    def _get_safe_error_message(self, e: Exception) -> str:
        try:
            return str(e)
        except Exception:
            try:
                msg = getattr(e, "message", None)
                if isinstance(msg, dict):
                    return f"Storage API Error: {msg.get('error', 'Unknown')} (Status: {msg.get('statusCode', 'Unknown')})"
                return f"Storage API Error: {msg}"
            except Exception:
                return "Unknown storage client error (likely HTTP 402 Payment Required or quota limits exceeded)"

    async def ensure_bucket(self):
        """Ensures the motu-catalog bucket exists and is public."""
        if not self.client or self.storage_disabled: return False
        try:
            # Check if bucket exists
            buckets = await asyncio.to_thread(self.client.storage.list_buckets)
            if not any(b.name == self.bucket_name for b in buckets):
                logger.info(f" Creating bucket: {self.bucket_name}")
                await asyncio.to_thread(self.client.storage.create_bucket, self.bucket_name, options={"public": True})
            return True
        except Exception as e:
            err_msg = self._get_safe_error_message(e)
            logger.error(f"❌ Error ensuring bucket: {err_msg}")
            if "402" in err_msg or "Payment" in err_msg or "quota" in err_msg or "attribute" in err_msg:
                logger.warning("⚠️ Disabling Supabase Storage integration due to quota limits / Payment Required.")
                self.storage_disabled = True
            return False

    def upload_image(self, local_path: str, folder: str = "") -> str:
        """
        Uploads a local image to Supabase Storage.
        Returns the public URL of the uploaded image.
        """
        if not self.client or self.storage_disabled: 
             logger.warning("⚠️ Storage client not initialized or disabled. Skipping upload.")
             return None
             
        path = Path(local_path)
        if not path.exists():
            logger.warning(f"⚠️ Local image not found: {local_path}")
            return None

        temp_webp_path = None
        # Convert to real WebP whenever extension isn't .webp OR magic bytes aren't RIFF...WEBP
        needs_webp_conversion = path.suffix.lower() != ".webp" or not has_webp_magic(path)
        if needs_webp_conversion:
            try:
                temp_webp_path = str(path.with_suffix(".temp.webp"))
                encode_webp_file(local_path, temp_webp_path, quality=85)
                upload_file_path = temp_webp_path
                file_name = path.stem + ".webp"
                content_type = "image/webp"
            except Exception as e:
                logger.warning(f"⚠️ Failed to convert {local_path} to WebP before upload: {e}")
                upload_file_path = local_path
                file_name = path.name
                content_type = "image/jpeg"
        else:
            upload_file_path = local_path
            file_name = path.name
            content_type = "image/webp"

        path_in_bucket = f"{folder}/{file_name}" if folder else file_name
        
        try:
            # Upload file
            with open(upload_file_path, "rb") as f:
                # We overwrite if exists to ensure latest version
                self.client.storage.from_(self.bucket_name).upload(
                    path_in_bucket, 
                    f, 
                    file_options={"upsert": "true", "content-type": content_type}
                )
            
            # Get Public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(path_in_bucket)
            logger.info(f"✅ Image uploaded: {path_in_bucket} -> {public_url}")
            return public_url
            
        except Exception as e:
            err_msg = self._get_safe_error_message(e)
            logger.error(f"❌ Error uploading {path_in_bucket}: {err_msg}")
            if "402" in err_msg or "Payment" in err_msg or "quota" in err_msg or "attribute" in err_msg:
                logger.warning("⚠️ Disabling further Supabase Storage uploads due to quota limits.")
                self.storage_disabled = True
            return None
        finally:
            if temp_webp_path and os.path.exists(temp_webp_path):
                try:
                    os.remove(temp_webp_path)
                except Exception:
                    pass

    def upload_all_local_images(self, images_dir: str, folder: str = "") -> Dict[str, str]:
        """Syncs all images in the local folder to the cloud and returns {stem: public_url}."""
        uploaded: Dict[str, str] = {}
        if self.storage_disabled:
            logger.warning("⚠️ Supabase Storage is disabled. Skipping directory sync.")
            return uploaded
        logger.info(f"🔄 Syncing all images from {images_dir} to Cloud folder '{folder}'...")
        p = Path(images_dir)
        if not p.exists():
            return uploaded

        # Match both jpg, png, jpeg, and webp for extra robustness
        for ext in ("*.jpg", "*.png", "*.jpeg", "*.webp"):
            if self.storage_disabled:
                break
            for img_file in p.glob(ext):
                if self.storage_disabled:
                    break
                if img_file.name.endswith(".temp.webp"):
                    continue
                url = self.upload_image(str(img_file), folder=folder)
                if url:
                    uploaded[img_file.stem] = url

        logger.info(f"✅ Sync complete: {len(uploaded)} images pushed to Supabase.")
        return uploaded
