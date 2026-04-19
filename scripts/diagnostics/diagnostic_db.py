import os
from src.core.config import settings
from src.infrastructure.database_cloud import cloud_url, engine_cloud
from src.domain.models import ProductModel, CollectionItemModel, UserModel
from sqlalchemy.orm import Session

def run_diagnostic():
    print("=== ORACULO DIAGNOSTIC ===")
    print(f"SUPABASE_DATABASE_URL defined: {settings.SUPABASE_DATABASE_URL is not None}")
    print(f"DATABASE_URL defined: {settings.DATABASE_URL}")
    print(f"Effective Cloud URL: {cloud_url}")
    
    if "postgresql" in cloud_url:
        print("Status: Connected to CLOUD (Postgres/Supabase)")
    elif "sqlite" in cloud_url:
        print("Status: Connected to LOCAL (SQLite)")
    else:
        print("Status: UNKNOWN DB TYPE")

    try:
        from sqlalchemy.orm import sessionmaker
        SessionCloud = sessionmaker(bind=engine_cloud)
        with SessionCloud() as db:
            p_count = db.query(ProductModel).count()
            c_count = db.query(CollectionItemModel).count()
            u_count = db.query(UserModel).count()
            print(f"Database contains:")
            print(f" - Products: {p_count}")
            print(f" - Collection Items: {c_count}")
            print(f" - Users: {u_count}")
    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    run_diagnostic()
