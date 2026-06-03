import sqlite3
import os

def fix_images():
    db_path = 'oraculo.db'
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de datos local {db_path} no encontrada.")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Obtener todos los productos con urls de actionfigure411
    rows = c.execute("SELECT id, name, image_url FROM products WHERE image_url LIKE '%actionfigure411.com%'").fetchall()
    
    if not rows:
        print("[INFO] No se encontraron productos con URLs de ActionFigure411 en la base de datos local.")
        conn.close()
        return

    print(f"[INFO] Encontrados {len(rows)} productos con URLs de ActionFigure411.")
    
    updated_count = 0
    supabase_base = "https://stxjzolhpcinrbkltehy.supabase.co/storage/v1/object/public/motu-catalog/"

    for pid, name, url in rows:
        # Extraer el nombre del archivo al final de la URL
        filename = url.split('/')[-1]
        
        # Generar nueva URL en Supabase
        new_url = f"{supabase_base}{filename}"
        
        # Actualizar base de datos
        c.execute("UPDATE products SET image_url = ? WHERE id = ?", (new_url, pid))
        updated_count += 1
        
        if updated_count <= 5:
            print(f"  - [{updated_count}] ID: {pid} | {name}")
            print(f"    Antigua: {url}")
            print(f"    Nueva:   {new_url}\n")
            
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Sincronización completada. Se han corregido {updated_count} URLs de imágenes en {db_path}.")

if __name__ == "__main__":
    fix_images()
