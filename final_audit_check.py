import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_sqlite():
    print("Checking SQLite...")
    conn = sqlite3.connect('oraculo.db')
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(kaizen_insights)")
    cols = [row[1] for row in cur.fetchall()]
    print(f"kaizen_insights columns: {cols}")
    conn.close()

def check_supabase():
    print("\nChecking Supabase...")
    url = os.getenv("SUPABASE_DATABASE_URL")
    if not url:
        print("SUPABASE_DATABASE_URL missing")
        return
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'kaizen_insights'")
    cols = [row[0] for row in cur.fetchall()]
    print(f"kaizen_insights columns: {cols}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        check_sqlite()
        check_supabase()
    except Exception as e:
        print(f"Error: {e}")
