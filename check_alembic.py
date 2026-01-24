import sqlite3
import os

db_path = "oraculo.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM alembic_version;")
        print(f"Alembic Version: {cursor.fetchall()}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
else:
    print("Database file not found.")
