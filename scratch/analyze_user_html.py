from bs4 import BeautifulSoup
import re

with open("scratch/user_smyths_html.html", "r", encoding="utf-8") as f:
    html = f.read()

print(f"HTML Length: {len(html)}")
soup = BeautifulSoup(html, "html.parser")

# Let's search for the product name
print("\nProduct Name Search:")
# Check h1 tag
h1s = soup.find_all("h1")
for h1 in h1s:
    print(f"  <h1>: '{h1.get_text(strip=True)}' classes='{h1.get('class')}'")
    
# Let's search for the price
print("\nPrice Search:")
# Search for numbers with decimal and currency sign, or class containing 'price'
price_elements = []
for tag in soup.find_all(True):
    txt = tag.get_text(strip=True)
    if "€" in txt or "EUR" in txt or "preis" in str(tag.get("class")).lower() or "price" in str(tag.get("class")).lower():
        # Clean text
        cleaned_txt = txt[:100].replace('\n', ' ').strip()
        price_elements.append((tag.name, tag.get("class"), cleaned_txt))

for name, cls, txt in price_elements[:30]:
    print(f"  <{name} class='{cls}'>: '{txt}'")

# Search for images
print("\nImage Search:")
images = soup.find_all("img")
print(f"Total images found: {len(images)}")
for idx, img in enumerate(images[:20]):
    print(f"  Image {idx}: src='{img.get('src')}', data-src='{img.get('data-src')}', alt='{img.get('alt')}'")

# Search for EAN or SKU or Art.Nr.
print("\nEAN / SKU / Article Number Search:")
# Usually Smyths Toys has a class or text containing "Art.Nr." or "ref" or "sku"
text_nodes = soup.find_all(text=True)
for node in text_nodes:
    if "art.nr" in node.lower() or "artikelnr" in node.lower() or "ref:" in node.lower() or "sku" in node.lower():
        print(f"  Text found: '{node.strip()}' (Parent: <{node.parent.name} class='{node.parent.get('class')}'>)")
