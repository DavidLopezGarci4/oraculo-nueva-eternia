import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_DATABASE_URL")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    for table in ['scraper_status', 'scraper_execution_logs', 'kaizen_insights']:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'spider_name'")
        res = cur.fetchone()
        print(f"Table {table} has spider_name: {res is not None}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
