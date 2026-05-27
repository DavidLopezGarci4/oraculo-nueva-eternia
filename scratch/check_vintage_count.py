import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import ProductModel, CollectionItemModel

def check_count():
    db_url = settings.SUPABASE_DATABASE_URL
    if not db_url:
        print("Error: SUPABASE_DATABASE_URL is not set!")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    total_products = session.query(ProductModel).count()
    vintage_products = session.query(ProductModel).filter_by(is_vintage=True).count()
    acquired_vintage = session.query(CollectionItemModel).join(ProductModel).filter(ProductModel.is_vintage == True).count()
    
    print(f"Total Products in DB: {total_products}")
    print(f"Vintage Products in DB (is_vintage=True): {vintage_products}")
    print(f"Acquired Vintage Items in Collection: {acquired_vintage}")
    
    if vintage_products > 0:
        print("\nSome sample vintage products:")
        samples = session.query(ProductModel).filter_by(is_vintage=True).limit(5).all()
        for p in samples:
            print(f"- ID: {p.id} | Figure ID: {p.figure_id} | Name: {p.name} | Category: {p.category} | Sub: {p.sub_category} | Price: {p.avg_market_price} | Img: {p.image_url}")
            
    session.close()

if __name__ == "__main__":
    check_count()
