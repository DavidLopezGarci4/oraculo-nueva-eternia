import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import ProductModel

def find_misplaced_vintage():
    db_url = settings.SUPABASE_DATABASE_URL
    if not db_url:
        print("Error: SUPABASE_DATABASE_URL is not set!")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Find products where is_vintage is True but sub_category or context indicates they are Origins/Modern
    misplaced = session.query(ProductModel).filter(
        ProductModel.is_vintage == True,
        ~ProductModel.sub_category.ilike("%vintage%")
    ).all()

    print("--- Misplaced Vintage Products (is_vintage=True but sub_category does not contain 'vintage') ---")
    for p in misplaced:
        print(f"ID: {p.id} | Figure ID: {p.figure_id} | Name: {p.name} | Sub: {p.sub_category} | Cat: {p.category}")

    session.close()

if __name__ == "__main__":
    find_misplaced_vintage()
