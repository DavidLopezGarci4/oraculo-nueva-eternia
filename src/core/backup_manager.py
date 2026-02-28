import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("backup_manager")

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class BackupManager:
    """
    The Data Fortress of Eternia.
    Handles raw data snapshots, versioned DB backups, and emergency restoration.
    """
    def __init__(self, base_path: str = "backups"):
        self.base_path = Path(base_path)
        self.snapshots_path = self.base_path / "raw_snapshots"
        self.db_backups_path = self.base_path / "database"
        
        # Ensure directory structure
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        self.db_backups_path.mkdir(parents=True, exist_ok=True)

    def save_raw_snapshot(self, shop_name: str, offers: List[Any]):
        """
        Saves the raw scraped data before any processing.
        Acts as the 'Flight Recorder' for scrapers.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"raw_{shop_name}_{timestamp}.json"
        
        # Convert ScrapedOffer objects to dicts if needed
        serializable_offers = []
        for o in offers:
            if hasattr(o, '__dict__'):
                data = o.__dict__.copy()
                # Ensure complex objects like URLs are strings
                if 'url' in data: data['url'] = str(data['url'])
                serializable_offers.append(data)
            else:
                serializable_offers.append(o)

        file_path = self.snapshots_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(serializable_offers, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)
            logger.info(f"🛡️ Raw snapshot saved: {filename} ({len(offers)} items)")
            
            # Retention: Keep only last 15 snapshots
            self._rotate_backups(self.snapshots_path, 15)
            
        except Exception as e:
            logger.error(f"❌ Failed to save raw snapshot: {e}")

    def create_database_backup(self, db_session):
        """
        [DEPRECATED/OPTIMIZED] Exports critical tables to JSON.
        Disabled to prevent excessive Egress bandwidth in Supabase.
        Supabase provides native daily backups for free.
        """
        logger.info("🏰 Database Vault generation bypassed (Delegated to Supabase Native Backups).")
        return None

    def _rotate_backups(self, folder: Path, limit: int):
        """Removes oldest files if limit exceeded."""
        files = sorted(list(folder.glob("*.json")), key=os.path.getmtime)
        if len(files) > limit:
            for f in files[:-limit]:
                os.remove(f)
                logger.info(f"🗑️ Rotated old backup: {f.name}")
