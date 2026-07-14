import sqlite3

conn = sqlite3.connect('oraculo.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]
print("Total productos:", count)

cursor.execute("SELECT id, name, figure_id, image_url FROM products LIMIT 10")
rows = cursor.fetchall()
print("\nPrimeros 10 productos:")
for r in rows:
    print(r)

conn.close()
