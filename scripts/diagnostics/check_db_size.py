import sqlite3
import os

db_path = "oraculo.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pending_matches")
    pending_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]
    
    print(f"Pending matches: {pending_count}")
    print(f"Products in catalog: {products_count}")
    print(f"Total match calculations per request: {pending_count * products_count}")
    
    conn.close()
