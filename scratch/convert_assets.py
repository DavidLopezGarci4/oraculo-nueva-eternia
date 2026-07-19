import os
import sys
import subprocess

def check_dependencies():
    try:
        from PIL import Image
        print("Pillow library is already installed.")
    except ImportError:
        print("Pillow not found. Installing Pillow library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])

def convert_to_webp():
    from PIL import Image
    
    assets_dir = os.path.join("frontend", "src", "assets")
    if not os.path.exists(assets_dir):
        print(f"Error: Assets directory {assets_dir} not found.")
        return
        
    images_to_convert = [
        "GlassmorphSwordHeMan.png",
        "HemanGlassmorphSword.png",
        "Entrance_prod.png",
        "bg-heman.png",
        "role-guardian.png",
        "role-master.png",
        "logo-nueva-eternia.png"
    ]
    
    total_saved = 0
    
    print("\n--- STARTING WEBP CONVERSION ---")
    for img_name in images_to_convert:
        png_path = os.path.join(assets_dir, img_name)
        if not os.path.exists(png_path):
            print(f"Skip: {img_name} not found.")
            continue
            
        base_name, _ = os.path.splitext(img_name)
        webp_path = os.path.join(assets_dir, f"{base_name}.webp")
        
        orig_size = os.path.getsize(png_path)
        
        # Open and save as WebP with 80% quality
        with Image.open(png_path) as img:
            img.save(webp_path, "WEBP", quality=80)
            
        new_size = os.path.getsize(webp_path)
        saved = orig_size - new_size
        total_saved += saved
        
        print(f"Converted '{img_name}':")
        print(f"  Original: {orig_size / 1024:.1f} KB")
        print(f"  WebP:     {new_size / 1024:.1f} KB")
        print(f"  Saved:    {saved / 1024:.1f} KB ({saved/orig_size*100:.1f}% reduction)")
        
    print(f"\n--- SUCCESS ---")
    print(f"Total Disk Space Saved: {total_saved / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    check_dependencies()
    convert_to_webp()
