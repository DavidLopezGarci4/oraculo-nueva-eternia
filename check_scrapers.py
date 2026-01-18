import sys
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

from src.infrastructure.database_cloud import SessionCloud as Session
from src.domain.models import ScraperStatusModel

def check_status():
    with Session() as db:
        statuses = db.query(ScraperStatusModel).all()
        print(f"Total scrapers in DB: {len(statuses)}")
        for s in statuses:
            print(f"- {s.spider_name}: {s.status}")

if __name__ == "__main__":
    check_status()
