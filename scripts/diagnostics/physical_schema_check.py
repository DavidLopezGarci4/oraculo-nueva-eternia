
from src.infrastructure.database_cloud import engine_cloud
from sqlalchemy import text

def inspect_schema():
    with engine_cloud.connect() as conn:
        for table in ['scraper_status', 'scraper_execution_logs']:
            print(f"\n--- Columns in {table} ---")
            query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
            res = conn.execute(text(query))
            for row in res:
                print(row[0])

if __name__ == "__main__":
    inspect_schema()
