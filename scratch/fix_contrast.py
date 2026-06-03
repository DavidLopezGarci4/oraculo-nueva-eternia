import re
import os

files_to_fix = [
    r"frontend/src/components/CollectionItemDetailModal.tsx",
    r"frontend/src/pages/Catalog.tsx",
    r"frontend/src/pages/Collection.tsx",
    r"frontend/src/pages/Config.tsx",
    r"frontend/src/pages/Dashboard.tsx",
    r"frontend/src/pages/Purgatory.tsx"
]

base_dir = r"c:\Users\dace8\OneDrive\Documentos\Antigravity\oraculo-nueva-eternia"

replacements = {
    "text-white/30": "text-white/60",
    "text-white/40": "text-white/65",
    "text-gray-400": "text-white/70"
}

for rel_path in files_to_fix:
    full_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(full_path):
        print(f"Skipping {rel_path} (does not exist)")
        continue
    
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    modified = False
    new_content = content
    for old, new in replacements.items():
        if old in new_content:
            new_content = new_content.replace(old, new)
            print(f"Replaced {old} with {new} in {rel_path}")
            modified = True
            
    if modified:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Saved changes to {rel_path}")
    else:
        print(f"No replacements needed in {rel_path}")
