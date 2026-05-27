import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import UserModel

def check_users():
    db_url = settings.SUPABASE_DATABASE_URL
    if not db_url:
        print("Error: SUPABASE_DATABASE_URL is not set!")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    users = session.query(UserModel).all()
    print("--- Users in DB ---")
    for u in users:
        print(f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Role: {u.role}")

    session.close()

if __name__ == "__main__":
    check_users()
