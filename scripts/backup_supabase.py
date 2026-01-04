
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

# Add src to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import (
    Base, UserModel, ProductModel, CollectionItemModel, 
    OfferModel, ScraperExecutionLogModel, ScraperStatusModel
)

def backup_cloud_data(cloud_db_url, backup_file="supabase_backup.db"):
    """
    Downloads data from Cloud (Supabase) to a local SQLite backup file.
    """
    if not cloud_db_url or "sqlite" in cloud_db_url:
        logger.error("❌ Invalid Cloud DB URL. Provide a Postgres URL.")
        return

    logger.info(f"🚀 Starting Backup from Cloud: {cloud_db_url.split('@')[1] if '@' in cloud_db_url else 'Remote'}")

    # 1. Cloud Source (Postgres)
    if cloud_db_url.startswith("postgres://"):
        cloud_db_url = cloud_db_url.replace("postgres://", "postgresql://", 1)
        
    cloud_engine = create_engine(cloud_db_url)
    CloudSession = sessionmaker(bind=cloud_engine)
    cloud_session = CloudSession()

    # 2. Local Backup (SQLite)
    backup_db_url = f"sqlite:///./{backup_file}"
    # Delete previous backup if exists
    if os.path.exists(backup_file):
        os.remove(backup_file)
        
    backup_engine = create_engine(backup_db_url)
    Base.metadata.create_all(backup_engine)
    BackupSession = sessionmaker(bind=backup_engine)
    backup_session = BackupSession()

    try:
        # Order matters for Foreign Keys
        tables = [
            (UserModel, "Users"),
            (ProductModel, "Products"),
            (OfferModel, "Offers"),
            (CollectionItemModel, "Collection Items"),
            (ScraperExecutionLogModel, "Logs"),
            (ScraperStatusModel, "Status")
        ]

        for model, label in tables:
            logger.info(f"📥 Downloading {label}...")
            items = cloud_session.query(model).all()
            for item in items:
                # We need to detach from cloud_session and merge into backup_session
                # But merge handles detached objects fine.
                backup_session.merge(item)
            backup_session.flush()
            logger.info(f"✅ {len(items)} {label} backed up.")

        backup_session.commit()
        logger.info(f"✨ Backup complete! Saved to {backup_file}")

    except Exception as e:
        logger.error(f"❌ Backup Failed: {e}")
        backup_session.rollback()
    finally:
        cloud_session.close()
        backup_session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Cloud Database URL (Postgres)")
    parser.add_argument("--out", default="supabase_backup.db", help="Backup filename")
    args = parser.parse_args()
    
    # Priority: CLI Arg > Environment Variable (SUPABASE_URL or DATABASE_URL if it's postgres)
    cloud_url = args.url or os.getenv("SUPABASE_URL") or settings.DATABASE_URL
    
    if "sqlite" in cloud_url:
        logger.warning("DATABASE_URL is SQLite. Set SUPABASE_URL in .env or use --url.")
    else:
        backup_cloud_data(cloud_url, args.out)
