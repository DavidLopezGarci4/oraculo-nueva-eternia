import shutil
import os
import logging
from datetime import datetime

logger = logging.getLogger("backup_adapter")

def create_db_backup(db_file="oraculo.db", backup_dir="backups", max_backups=7):
    """
    Creates a timestamped backup of the database and rotates old ones.
    """
    try:
        if not os.path.exists(db_file):
            logger.warning(f"⚠️ Backup source not found: {db_file}")
            return None
            
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(backup_dir, f"oraculo_{timestamp}.db")
        
        shutil.copy2(db_file, backup_path)
        logger.info(f"🛡️ Backup created: {backup_path}")
        
        # Rotation
        files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db")]
        files.sort(key=os.path.getmtime)
        
        if len(files) > max_backups:
            for f_to_del in files[:-max_backups]:
                os.remove(f_to_del)
                logger.info(f"🗑️ Rotated old backup: {f_to_del}")
                
        return backup_path
    except Exception as e:
        logger.error(f"⚠️ Backup failed: {e}")
        return None
