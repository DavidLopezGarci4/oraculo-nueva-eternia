import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.core.config import settings
from src.domain.models import ProductModel, CollectionItemModel

def fix_misplaced_figures():
    db_url = settings.SUPABASE_DATABASE_URL
    if not db_url:
        print("Error: SUPABASE_DATABASE_URL is not set!")
        return

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find products to fix
        target_ids = [1249, 943]
        products = session.query(ProductModel).filter(ProductModel.id.in_(target_ids)).all()
        
        print("--- Before Update ---")
        for p in products:
            print(f"Product ID: {p.id} | Figure ID: {p.figure_id} | Name: {p.name} | is_vintage: {p.is_vintage} | Sub: {p.sub_category}")
            
        print("\nUpdating is_vintage to False for these products...")
        for p in products:
            p.is_vintage = False
            
        # Find any other products with modern categories that are accidentally marked as vintage
        other_misplaced = session.query(ProductModel).filter(
            ProductModel.is_vintage == True,
            ProductModel.sub_category.ilike("Origins%")
        ).all()
        
        if other_misplaced:
            print(f"\nFound {len(other_misplaced)} other misplaced Origins products:")
            for p in other_misplaced:
                print(f"- ID: {p.id} | Figure ID: {p.figure_id} | Name: {p.name} | Sub: {p.sub_category}")
                p.is_vintage = False
                
        session.commit()
        print("\n✅ Database updated successfully! Committed changes.")
        
        # Verify collection item locations
        print("\nVerifying current locations of collection items for these product IDs:")
        for pid in target_ids:
            items = session.query(CollectionItemModel).filter_by(product_id=pid).all()
            print(f"Product ID {pid}: Found {len(items)} items in users' collections.")
            for item in items:
                print(f"  - Item ID: {item.id} | Owner ID: {item.owner_id} | Acquired: {item.acquired} | Notes: {item.notes}")
                
    except Exception as e:
        session.rollback()
        print(f"❌ Error updating database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_misplaced_figures()
