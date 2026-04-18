from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_DATABASE_URL")

if not url:
    print("SUPABASE_DATABASE_URL not found")
else:
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT shop_name, COUNT(*) FROM pending_matches GROUP BY shop_name")).all()
        print("Shop Distribution in Purgatory:")
        for shop, count in res:
            print(f"- {shop}: {count}")
