import os
import shutil
import sqlite3

# Define paths
db_path = 'oraculo.db'
origins_dir = os.path.join('data', 'MOTU', 'images')
vintage_dir = os.path.join('data', 'MOTU', 'vintage_images')
cache_dir = os.path.join('data', 'image_cache')

os.makedirs(cache_dir, exist_ok=True)

# Connect to DB
conn = sqlite3.connect(db_path)
products = conn.execute('SELECT id, name, image_url, is_vintage FROM products;').fetchall()
conn.close()

copied = 0
not_found = []

for p in products:
    p_id, name, url, is_vintage = p
    if not url:
        continue
    
    fname = url.split('/')[-1]
    
    # Check in origins first, then vintage
    src_path = os.path.join(origins_dir, fname)
    if not os.path.exists(src_path):
        src_path = os.path.join(vintage_dir, fname)
        
    dest_path = os.path.join(cache_dir, f"{p_id}.jpg")
    
    if os.path.exists(src_path):
        shutil.copy2(src_path, dest_path)
        copied += 1
    else:
        not_found.append((p_id, name, fname))

print(f"Total products processed: {len(products)}")
print(f"Successfully copied to cache: {copied}")
print(f"Not found in local folders: {len(not_found)}")
if not_found:
    print("Not found details (first 10):")
    for nf in not_found[:10]:
        print(nf)
