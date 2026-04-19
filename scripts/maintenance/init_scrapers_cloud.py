
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel
from datetime import datetime

def initialize_scrapers():
    scrapers = [
        "ActionToys", "Amazon.es", "DeToyboys", "Ebay.es", 
        "Fantasia Personajes", "Frikiverso", "Electropolis", 
        "Pixelatoy", "ToymiEU", "Time4ActionToysDE", "BigBadToyStore"
    ]
    
    with SessionCloud() as db:
        for name in scrapers:
            status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == name).first()
            if not status:
                print(f"Initializing {name}...")
                status = ScraperStatusModel(
                    spider_name=name,
                    status="idle",
                    last_update=datetime.utcnow()
                )
                db.add(status)
            else:
                # If it's in error, let's reset it to idle for the user to try again
                if "error" in status.status.lower():
                    print(f"Resetting {name} from error to idle...")
                    status.status = "idle"
                    status.last_update = datetime.utcnow()
        
        db.commit()
        print("Scrapers initialized/reset successfully.")

if __name__ == "__main__":
    initialize_scrapers()
