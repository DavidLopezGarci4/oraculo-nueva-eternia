from bs4 import BeautifulSoup
import re

with open("scratch/smyths_headed_success.html", "r", encoding="utf-8") as f:
    html = f.read()

print(f"HTML Length: {len(html)}")
soup = BeautifulSoup(html, "html.parser")

# Print page title
print(f"Page Title: {soup.title.string if soup.title else 'None'}")

# Print first 1000 characters of body text
body_text = soup.body.get_text() if soup.body else ""
print("Body snippet:")
print(body_text[:1000].replace('\n', ' ').strip())

# Check for links or any elements
print(f"Total elements: {len(soup.find_all())}")
print(f"Total <a> tags: {len(soup.find_all('a'))}")
print(f"Total <div> tags: {len(soup.find_all('div'))}")

# Let's search if there's any JSON content or script block containing product data
scripts = soup.find_all("script")
print(f"Total <script> tags: {len(scripts)}")
for idx, s in enumerate(scripts):
    src = s.get("src", "")
    content = s.string or ""
    if "MOTU" in content or "Masters of the Universe" in content or "price" in content.lower():
        print(f"  Script {idx} (src='{src}'): contains keywords! Length: {len(content)}")
        print(f"  Snippet: {content[:200].strip()}")
