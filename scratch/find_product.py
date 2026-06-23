import sqlite3

conn = sqlite3.connect('oraculo.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, image_url FROM products WHERE name LIKE '%Stone%';")
for row in cursor.fetchall():
    print(row)
conn.close()
