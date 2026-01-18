import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

from src.infrastructure.database_cloud import SessionCloud as Session
from src.domain.models import ScraperStatusModel

def init_scrapers():
    scrapers = [
        "ActionToys", "Fantasia", "Frikiverso", "Electropolis", 
        "Pixelatoy", "amazon", "dvdstorespain", "kidinn",
        "DeToyboys", "MotuClassicsDE", "VendiloshopIT", 
        "ToymiEU", "Time4ActionToysDE", "BigBadToyStore"
    ]
    
    with Session() as db:
        for name in scrapers:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == name).first()
            if not status:
                print(f"Creating status for {name}...")
                status = ScraperStatusModel(
                    spider_name=name,
                    status="idle",
                    last_update=datetime.utcnow()
                )
                db.add(status)
            else:
                print(f"Scraper {name} already exists with status: {status.status}")
        
        db.commit()
    print("Initialization complete.")

if __name__ == "__main__":
    init_scrapers()
