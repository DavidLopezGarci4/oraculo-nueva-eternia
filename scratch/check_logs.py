import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root dir to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import ScraperExecutionLogModel, ScraperStatusModel

def check_logs():
    db_url = settings.SUPABASE_DATABASE_URL
    print(f"Connecting to: {db_url.split('@')[-1] if db_url else 'None'}")
    
    if not db_url:
        print("Error: SUPABASE_DATABASE_URL is not set!")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("\n--- Scraper Status ---")
    statuses = session.query(ScraperStatusModel).all()
    for s in statuses:
        print(f"Spider: {s.spider_name} | Status: {s.status} | Start: {s.start_time} | End: {s.end_time}")

    print("\n--- Recent Execution Logs ---")
    logs = session.query(ScraperExecutionLogModel).order_by(ScraperExecutionLogModel.id.desc()).limit(5).all()
    for l in logs:
        info_str = f"\nID: {l.id} | Spider: {l.spider_name} | Status: {l.status} | Start: {l.start_time}\n"
        sys.stdout.buffer.write(info_str.encode('utf-8'))
        sys.stdout.buffer.write(b"Logs:\n")
        logs_str = (l.logs[-2000:] if l.logs else "No logs") + "\n"
        sys.stdout.buffer.write(logs_str.encode('utf-8'))
        sys.stdout.buffer.write(b"-" * 50 + b"\n")

    session.close()

if __name__ == "__main__":
    check_logs()
