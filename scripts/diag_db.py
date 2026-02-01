from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel

with SessionCloud() as db:
    scrapers = db.query(ScraperStatusModel).all()
    print("--- SCRAPER RECORDS ---")
    for s in scrapers:
        print(f"ID: {s.id} | Name: '{s.spider_name}' | Status: {s.status}")
