from bs4 import BeautifulSoup

def analyze_file(filename):
    print(f"\n=================== Analyzing {filename} ===================")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    
    # Check body length
    print(f"HTML Length: {len(html)}")
    
    # Find all product containers
    # Let's search for tags representing products
    # Smyths Toys uses standard web component/tag structures. Let's see all unique class names or tag names.
    # Let's count some elements
    print("Element Counts:")
    for tag_name in ['article', 'product-tile', 'smyths-product', 'div', 'a', 'span']:
        print(f"  - <{tag_name}>: {len(soup.find_all(tag_name))}")
        
    # Let's print the first 20 links in the page
    links = soup.find_all("a", href=True)
    print(f"Total links found: {len(links)}")
    print("Sample links:")
    sample_links = [l for l in links if "actionfiguren" in l["href"] or "masters-of-the-universe" in l["href"].lower() or "/de-de/" in l["href"]]
    for idx, l in enumerate(sample_links[:20]):
        print(f"  - {idx}: '{l.get_text(strip=True)[:40]}' -> {l['href']}")
        
    # Let's search for any link that ends with a number (common for product codes on Smyths, e.g. /de-de/.../p/123456 or just a code)
    # Actually, Smyths product URLs usually look like: /de/de-de/spielzeug/.../p/123456 or similar, let's look for `/p/` or see what links exist.
    # Let's print ALL links that look like a product page
    print("All links containing '/p/' or matching product pattern:")
    matched = 0
    for l in links:
        href = l["href"]
        if "/p/" in href or re.search(r'/\d{5,8}$', href) or "de-de" in href:
            # Let's see
            if "/de/de-de/" in href and not any(skip in href for skip in ["/c/", "/hilfe", "/store-finden"]):
                print(f"  - '{l.get_text(strip=True)[:40]}' -> {href}")
                matched += 1
                if matched >= 20: break
                
    # If no links found, let's print the first 20 links of any kind
    if matched == 0:
        print("First 20 links of any kind:")
        for idx, l in enumerate(links[:20]):
            print(f"  - {idx}: '{l.get_text(strip=True)[:40]}' -> {l['href']}")

import re
analyze_file("scratch/smyths_stealth.html")
