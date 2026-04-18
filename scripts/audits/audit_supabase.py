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
    
    cur.execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        ORDER BY table_name, ordinal_position
    """)
    columns = cur.fetchall()
    
    schema = {}
    for t, c in columns:
        schema.setdefault(t, []).append(c)
        
    for t, cols in schema.items():
        print(f"\n[{t}]")
        for col in cols:
            print(f"  - {col}")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
