import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

postgres_url = "postgresql://postgres.stxjzolhpcinrbkltehy:USe4i3LmtRBZw20A@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
sqlite_url = "sqlite:///oraculo.db"

pg_engine = create_engine(postgres_url)
sqlite_engine = create_engine(sqlite_url)

pg_metadata = MetaData()
sqlite_metadata = MetaData()

pg_metadata.reflect(bind=pg_engine)
sqlite_metadata.reflect(bind=sqlite_engine)

print("--- Data Sync: Supabase Cloud Postgres -> Local SQLite ---")

# Connect to sqlite using direct connection to ignore transaction issues during deletions
sqlite_conn = sqlite3.connect("oraculo.db")
sqlite_cursor = sqlite_conn.cursor()

# Disable foreign keys temporarily for bulk deletion and insert
sqlite_cursor.execute("PRAGMA foreign_keys = OFF;")

tables_to_sync = list(sqlite_metadata.tables.keys())
# Avoid syncing alembic_version since it manages migrations
if "alembic_version" in tables_to_sync:
    tables_to_sync.remove("alembic_version")

for table_name in tables_to_sync:
    if table_name not in pg_metadata.tables:
        print(f"Skipping {table_name}: not present in cloud database.")
        continue
        
    print(f"Syncing table: {table_name}...")
    
    # Get columns
    sqlite_table = sqlite_metadata.tables[table_name]
    columns = [c.name for c in sqlite_table.columns]
    col_str = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))
    
    # Clear local table
    sqlite_cursor.execute(f"DELETE FROM {table_name};")
    
    # Fetch from Postgres
    with pg_engine.connect() as pg_conn:
        pg_result = pg_conn.execute(sqlalchemy.text(f"SELECT {col_str} FROM {table_name};"))
        rows = pg_result.fetchall()
        
    # Insert into SQLite
    if rows:
        sqlite_cursor.executemany(
            f"INSERT OR REPLACE INTO {table_name} ({col_str}) VALUES ({placeholders});",
            [tuple(row) for row in rows]
        )
        print(f"  -> Copied {len(rows)} rows.")
    else:
        print("  -> Table is empty in cloud.")

sqlite_cursor.execute("PRAGMA foreign_keys = ON;")
sqlite_conn.commit()
sqlite_conn.close()

print("\nSync completed successfully!")
