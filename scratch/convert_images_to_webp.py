import os
import sqlite3
from PIL import Image

def convert_to_webp():
    cache_dir = os.path.join('data', 'image_cache')
    if not os.path.exists(cache_dir):
        print(f"[ERROR] Cache directory {cache_dir} does not exist.")
        return

    print(f"[INFO] Scanning {cache_dir} for images...")
    files = os.listdir(cache_dir)
    jpg_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not jpg_files:
        print("[INFO] No JPEG/PNG files found to convert.")
        return

    print(f"[INFO] Found {len(jpg_files)} files to convert to WebP.")
    converted_count = 0
    errors = 0
    original_size = 0
    new_size = 0

    for fname in jpg_files:
        filepath = os.path.join(cache_dir, fname)
        base_name, _ = os.path.splitext(fname)
        webp_filepath = os.path.join(cache_dir, f"{base_name}.webp")
        
        try:
            # Measure size
            fsize = os.path.getsize(filepath)
            original_size += fsize
            
            # Convert
            with Image.open(filepath) as img:
                # Convert RGBA to RGB if saving as JPEG/WebP to avoid issues, or keep transparency for WebP
                if img.mode in ('RGBA', 'LA') and fname.lower().endswith(('.jpg', '.jpeg')):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                
                # Save as webp
                img.save(webp_filepath, 'WEBP', quality=85)
            
            wsize = os.path.getsize(webp_filepath)
            new_size += wsize
            
            # Delete original
            os.remove(filepath)
            converted_count += 1
            
            if converted_count % 50 == 0 or converted_count == len(jpg_files):
                print(f"  - Converted {converted_count}/{len(jpg_files)} images...")
                
        except Exception as e:
            print(f"[ERROR] Failed to convert {fname}: {e}")
            errors += 1

    saved_mb = (original_size - new_size) / (1024 * 1024)
    original_mb = original_size / (1024 * 1024)
    new_mb = new_size / (1024 * 1024)

    print(f"\n[SUCCESS] WebP conversion completed!")
    print(f"  - Successfully converted: {converted_count}")
    print(f"  - Errors: {errors}")
    print(f"  - Original total size: {original_mb:.2f} MB")
    print(f"  - WebP total size: {new_mb:.2f} MB")
    print(f"  - Space saved: {saved_mb:.2f} MB ({((original_size - new_size)/original_size * 100) if original_size > 0 else 0:.1f}% reduction)")

if __name__ == "__main__":
    convert_to_webp()
