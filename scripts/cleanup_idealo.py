
import sys
import os
from pathlib import Path

# Add src to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel, Base

def clean_idealo():
    print("Starting Database Cleanup for Idealo...")
    
    with SessionCloud() as db:
        # 1. Delete all variants of idealo
        targets = ["Idealo.es", "idealo.es", "Idealo", "idealo"]
        
        deleted_count = 0
        for name in targets:
            item = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == name).first()
            if item:
                print(f"Found {name} (ID: {item.id}). Deleting...")
                db.delete(item)
                deleted_count += 1
        
        if deleted_count > 0:
            db.commit()
            print(f"Successfully deleted {deleted_count} Idealo records.")
        else:
            print("No Idealo records found in database.")

if __name__ == "__main__":
    clean_idealo()
