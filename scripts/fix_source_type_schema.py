import sqlite3
import os

def fix_schema():
    db_path = "oraculo.db"
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["offers", "pending_matches"]
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "origin_category" in columns and "source_type" not in columns:
            print(f"Renombrando origin_category a source_type en {table}...")
            # SQLite doesn't support RENAME COLUMN in older versions, but let's try (supported since 3.25)
            try:
                cursor.execute(f"ALTER TABLE {table} RENAME COLUMN origin_category TO source_type")
                print("Renombrado con éxito.")
            except Exception as e:
                print(f"Error renombrando: {e}. Intentando fallback...")
                # Fallback: Add column and move data if rename fails (shouldn't happen on modern systems)
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN source_type VARCHAR(20) DEFAULT 'Retail'")
                cursor.execute(f"UPDATE {table} SET source_type = origin_category")
        
        elif "source_type" not in columns:
             print(f"Añadiendo source_type a {table}...")
             cursor.execute(f"ALTER TABLE {table} ADD COLUMN source_type VARCHAR(20) DEFAULT 'Retail'")

    conn.commit()
    conn.close()
    print("Esquema corregido.")

if __name__ == "__main__":
    fix_schema()
