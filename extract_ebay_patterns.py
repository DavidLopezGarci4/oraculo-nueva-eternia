
import re

def extract_patterns(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"File size: {len(content)}")
    
    # Let's find "Vendido" and print context
    pos = content.find("Vendido")
    if pos != -1:
        print(f"Found 'Vendido' at {pos}")
        print("--- CONTEXT ---")
        print(content[pos-100:pos+200])
        
    # Let's find prices
    price_matches = re.findall(r'class="s-item__price">.*?</span>', content)
    if price_matches:
        print(f"\nFound {len(price_matches)} prices. Sample:")
        print(price_matches[0])

if __name__ == "__main__":
    extract_patterns("ebay_sold_audit.html")
