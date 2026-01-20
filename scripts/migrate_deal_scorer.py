import sqlite3
import os

def migrate():
    db_path = "oraculo.db"
    if not os.path.exists(db_path):
        print(f"No se encontró la base de datos en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["offers", "pending_matches"]
    
    for table in tables:
        try:
            print(f"Añadiendo columna 'opportunity_score' a la tabla '{table}'...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN opportunity_score INTEGER DEFAULT 0")
            print(f"Columna añadida con éxito a '{table}'.")
        except sqlite3.OperationalError:
            print(f"La columna 'opportunity_score' ya existe en '{table}' o hubo un error.")

    conn.commit()
    conn.close()
    print("Migración de DealScorer completada (Local).")

if __name__ == "__main__":
    migrate()
