import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_DATABASE_URL")

if not url:
    print("SUPABASE_DATABASE_URL not found")
    exit(1)

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    # List of renames and missing columns
    commands = [
        "ALTER TABLE scraper_status RENAME COLUMN spider_name TO scraper_name;",
        "ALTER TABLE scraper_execution_logs RENAME COLUMN spider_name TO scraper_name;",
        "ALTER TABLE kaizen_insights RENAME COLUMN spider_name TO scraper_name;",
    ]
    
    for cmd in commands:
        try:
            print(f"Executing: {cmd}")
            cur.execute(cmd)
            conn.commit()
            print("Success")
        except Exception as e:
            conn.rollback()
            print(f"Failed (likely already renamed): {e}")

    # Add other missing Phase 35 columns if any
    # Check users.location
    try:
        cur.execute("ALTER TABLE users ADD COLUMN location VARCHAR DEFAULT 'ES';")
        conn.commit()
        print("Added users.location")
    except Exception as e:
        conn.rollback()
        print(f"users.location skip: {e}")

    # Reset alembic_version to reflect the new state so it doesn't try to re-run
    try:
        # We'll use the version ID from our local migration
        version = 'e905ab7993c4'
        cur.execute("DELETE FROM alembic_version;")
        cur.execute(f"INSERT INTO alembic_version (version_num) VALUES ('{version}');")
        conn.commit()
        print(f"Stamped alembic_version to {version}")
    except Exception as e:
        conn.rollback()
        print(f"Alembic stamp skip: {e}")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"Main Error: {e}")
