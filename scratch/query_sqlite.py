import sqlite3
conn = sqlite3.connect('oraculo.db')
c = conn.cursor()
rows = c.execute("SELECT id, name, image_url FROM products WHERE name LIKE 'Orko%' OR name LIKE 'Panthor%' OR name LIKE 'Panthro%' OR name LIKE 'Pig%' OR name LIKE 'Prince Adam%' OR name LIKE 'Ram Man%' OR name LIKE 'Raphael%'").fetchall()
for r in rows:
    print(f"ID: {r[0]} | Name: {r[1]} | Image URL: {r[2]}")
conn.close()
