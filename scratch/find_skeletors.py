import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import ProductModel

def find_skeletors():
    db_url = settings.SUPABASE_DATABASE_URL
    if not db_url:
        print("Error: SUPABASE_DATABASE_URL is not set!")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    skeletors = session.query(ProductModel).filter(
        ProductModel.name.ilike("%skeletor%")
    ).all()

    print("--- Skeletors in DB ---")
    for p in skeletors:
        print(f"ID: {p.id} | Figure ID: {p.figure_id} | Name: {p.name} | is_vintage: {p.is_vintage} | Sub: {p.sub_category} | Cat: {p.category}")

    session.close()

if __name__ == "__main__":
    find_skeletors()
