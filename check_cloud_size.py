from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_DATABASE_URL")

if not url:
    print("SUPABASE_DATABASE_URL not found in .env")
else:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            p_count = conn.execute(text("SELECT COUNT(*) FROM pending_matches")).scalar()
            prod_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            print(f"Cloud Pending: {p_count}")
            print(f"Cloud Products: {prod_count}")
    except Exception as e:
        print(f"Cloud Error: {e}")
