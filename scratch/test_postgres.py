import sqlalchemy
from sqlalchemy import create_engine

url = "postgresql://postgres.stxjzolhpcinrbkltehy:USe4i3LmtRBZw20A@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

print("Attempting to connect to Supabase Postgres...")
try:
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    with engine.connect() as conn:
        print("Connection successful!")
        # Let's see the tables
        result = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM products;"))
        print("Products count in Supabase:", result.fetchone()[0])
        result = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM collection_items;"))
        print("Collection items count in Supabase:", result.fetchone()[0])
except Exception as e:
    print("Connection failed:", e)
