import sqlite3
import os
from src.core.config import settings
from sqlalchemy import create_engine, text

def diagnostic():
    print("--- DIAGNOSTICO DE DATOS ---")
    
    # 1. LOCAL SQLITE
    db_path = "oraculo.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM offers")
        print(f"Local SQLite (offers): {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM products")
        print(f"Local SQLite (products): {cursor.fetchone()[0]}")
        conn.close()
    else:
        print("Local SQLite not found.")

    # 2. CLOUD SUPABASE
    if settings.SUPABASE_DATABASE_URL:
        try:
            engine = create_engine(settings.SUPABASE_DATABASE_URL)
            with engine.connect() as conn:
                res = conn.execute(text("SELECT COUNT(*) FROM offers"))
                print(f"Cloud Supabase (offers): {res.scalar()}")
                
                # Check column names
                res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'offers'"))
                cols = [r[0] for r in res.fetchall()]
                print(f"Cloud Columns: {cols}")
                
                source_col = "source_type" if "source_type" in cols else "origin_category"
                res = conn.execute(text(f"SELECT {source_col}, COUNT(*) FROM offers GROUP BY {source_col}"))
                print(f"\nCloud Stats by {source_col}:")
                res = conn.execute(text(f"SELECT COUNT(*) FROM offers WHERE opportunity_score > 0"))
                print(f"  Offers with Score > 0: {res.scalar()}")
                res = conn.execute(text(f"SELECT COUNT(*) FROM products WHERE retail_price > 0"))
                print(f"  Products with MSRP > 0: {res.scalar()}")
                res = conn.execute(text(f"SELECT COUNT(*) FROM products WHERE p25_price > 0"))
                print(f"  Products with P25 > 0: {res.scalar()}")
        except Exception as e:
            print(f"Error connecting to Cloud: {e}")
    else:
        print("SUPABASE_DATABASE_URL not set.")

if __name__ == "__main__":
    diagnostic()
