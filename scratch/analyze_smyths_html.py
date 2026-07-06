from bs4 import BeautifulSoup
import re

def analyze_file(filename):
    print(f"\n=================== Analyzing {filename} ===================")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    
    # Check if blocked
    body_text = soup.body.get_text() if soup.body else ""
    if "additional security check" in body_text.lower() or "imperva" in body_text.lower() or "incapsula" in body_text.lower():
        print("[BLOCKED] BLOCKED by Imperva WAF!")
        print(body_text[:500].strip())
        return
        
    print("[OK] Clear page (Not blocked)!")
    
    # Print first 500 characters of body text
    print("Body text snippet:")
    print(body_text[:500].replace('\n', ' ').strip())
    
    # Print some links
    links = soup.find_all("a", href=True)
    product_links = []
    for l in links:
        href = l["href"]
        if "/p/" in href or "de-de/" in href or "motu" in href.lower() or "masters-of-the-universe" in href.lower():
            product_links.append((l.get_text(strip=True), href))
            
    print(f"Total links: {len(links)}")
    print(f"Sample product/category-ish links (showing up to 10):")
    for txt, href in product_links[:10]:
        print(f"  - '{txt}': {href}")
        
    product_containers = []
    for tag in soup.find_all(class_=True):
        classes = tag.get("class", [])
        classes_str = " ".join(classes)
        if any(w in classes_str.lower() for w in ["product", "item", "grid-item", "card"]):
            if len(tag.select("a[href*='/p/']")) > 0 or len(tag.select("a[href*='de-de']")) > 0:
                product_containers.append((tag.name, classes_str))
                
    print(f"Found {len(product_containers)} possible product container elements. Sample classes:")
    for name, cls in list(set(product_containers))[:15]:
        print(f"  - <{name} class='{cls}'>")
        
    p_links = soup.select("a[href*='/p/']")
    print(f"Found {len(p_links)} links containing '/p/'")
    for idx, pl in enumerate(p_links[:10]):
        print(f"  - {idx}: '{pl.get_text(strip=True)}' -> {pl.get('href')}")
        # Print parent elements classes
        curr = pl.parent
        hierarchy = []
        for _ in range(4):
            if not curr: break
            hierarchy.append(f"<{curr.name} class='{' '.join(curr.get('class', []))[:50]}'>")
            curr = curr.parent
        print(f"    Hierarchy: {' -> '.join(hierarchy)}")

analyze_file("scratch/smyths_curl.html")
analyze_file("scratch/smyths_playwright.html")
analyze_file("scratch/smyths_scraperapi.html")
