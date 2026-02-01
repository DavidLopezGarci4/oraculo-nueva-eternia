
import sys
import os
from pathlib import Path

# Add src to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel, Base

def clean_harvester():
    print("Starting Database Cleanup for Harvester...")
    
    with SessionCloud() as db:
        # 1. Check if Harvester exists
        harvester = db.query(ScraperStatusModel).filter(
            (ScraperStatusModel.spider_name == "harvester") | 
            (ScraperStatusModel.spider_name == "Harvester")
        ).first()
        
        if harvester:
            print(f"Found Harvester (ID: {harvester.id}). Deleting...")
            db.delete(harvester)
            db.commit()
            print("✅ Harvester deleted successfully.")
        else:
            print("✅ Harvester not found in database.")

if __name__ == "__main__":
    clean_harvester()
