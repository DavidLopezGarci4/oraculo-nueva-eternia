
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel
from sqlalchemy import desc

def check_db():
    with SessionCloud() as db:
        print("--- Scraper Status ---")
        statuses = db.query(ScraperStatusModel).all()
        for s in statuses:
            print(f"ID: {s.id} | Name: {s.spider_name} | Status: {s.status} | Last: {s.last_update}")
            
        print("\n--- Recent Execution Logs ---")
        logs = db.query(ScraperExecutionLogModel).order_by(desc(ScraperExecutionLogModel.start_time)).limit(10).all()
        for l in logs:
            print(f"ID: {l.id} | Name: {l.spider_name} | Status: {l.status} | Time: {l.start_time}")

if __name__ == "__main__":
    check_db()
