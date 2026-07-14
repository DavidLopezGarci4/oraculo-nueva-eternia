import sqlite3

conn = sqlite3.connect('oraculo.db')
cursor = conn.cursor()

ids = (13977, 13978, 14038, 14039)
cursor.execute("SELECT id, name, figure_id, image_url FROM products WHERE id IN (?, ?, ?, ?)", ids)
rows = cursor.fetchall()

print("REGISTROS EN DB LOCAL:")
for row in rows:
    print(f"ID: {row[0]} | Name: {row[1]} | Figure ID: {row[2]} | Image URL: {row[3]}")

conn.close()
