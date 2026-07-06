from bs4 import BeautifulSoup

with open("scratch/smyths_blocked_clean_ua.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
body_text = soup.body.get_text() if soup.body else ""

print(f"HTML Length: {len(html)}")
print(f"Page Title: {soup.title.string if soup.title else 'None'}")
print("Body snippet:")
print(body_text[:1000].replace('\n', ' ').strip())
