import sqlite3
import os

def audit_db():
    db_path = "oraculo.db"
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"--- GLOBAL COUNTS ---")
    for table in ["products", "offers", "pending_matches", "collection_items"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table}: {cursor.fetchone()[0]}")

    print("\n--- AUDITORÍA DE COLUMNAS (offers) ---")
    cursor.execute("PRAGMA table_info(offers)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columnas detectadas: {columns}")

    src_col = "source_type" if "source_type" in columns else ("origin_category" if "origin_category" in columns else None)

    if src_col:
        print(f"\n--- CONTEO POR {src_col} ---")
        cursor.execute(f"SELECT {src_col}, COUNT(*) FROM offers GROUP BY {src_col}")
        for row in cursor.fetchall():
            print(f"{src_col}: {row[0]} | Count: {row[1]}")
    else:
        print("\nERROR: No se detectó columna de categoría de origen.")

    print("\n--- ESTADO DE DISPONIBILIDAD ---")
    if "is_available" in columns:
        cursor.execute("SELECT is_available, COUNT(*) FROM offers GROUP BY is_available")
        for row in cursor.fetchall():
            print(f"is_available: {row[0]} | Count: {row[1]}")

    conn.close()

if __name__ == "__main__":
    audit_db()
