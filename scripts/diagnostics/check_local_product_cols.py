
import sqlite3

def check_product_columns():
    conn = sqlite3.connect("oraculo.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(products);")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Columns in local products table: {columns}")
    conn.close()

if __name__ == "__main__":
    check_product_columns()
