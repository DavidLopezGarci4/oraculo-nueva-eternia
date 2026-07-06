import os

path = "scratch/last_msg.txt"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"File length: {len(content)}")
    print(f"Snippet of first 200 chars: {content[:200]}")
    # Search for some tags
    for tag in ["body", "smyths", "class=", "spielzeug", "actionfiguren", "price", "EUR", "preis"]:
        found_idx = content.lower().find(tag.lower())
        print(f"Search for '{tag}': found at index {found_idx}")
        if found_idx != -1:
            print(f"  Context: {content[found_idx:found_idx+150]}")
else:
    print("last_msg.txt not found!")
