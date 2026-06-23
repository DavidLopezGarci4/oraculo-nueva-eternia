import os
import sqlite3

conn = sqlite3.connect('oraculo.db')
products = conn.execute('SELECT id, name, image_url FROM products;').fetchall()
conn.close()

local_files = os.listdir('data/MOTU/images')
matched = 0
not_found = []

for p in products:
    url = p[2]
    if url:
        fname = url.split('/')[-1]
        if fname in local_files:
            matched += 1
        else:
            not_found.append((p[0], p[1], fname))

print(f"Total products: {len(products)}")
print(f"Matched locally in data/MOTU/images: {matched}")
print(f"Not matched: {len(not_found)}")
if not_found:
    print("Some unmatched samples:")
    for nf in not_found[:10]:
        print(nf)
