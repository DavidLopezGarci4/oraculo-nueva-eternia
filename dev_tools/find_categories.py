from playwright.sync_api import sync_playwright

def find_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Fantasia
        print("Visiting Fantasia Personajes Home...")
        page.goto("https://fantasiapersonajes.es/")
        page.wait_for_timeout(3000)
        
        # Extract all links
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText,
                href: a.href
            }));
        }""")
        
        print(f"Found {len(links)} links. Filtering for 'Masters'...")
        for l in links:
            if "Masters" in l['text'] or "He-Man" in l['text']:
                try:
                    print(f"FOUND: {l['text']} -> {l['href']}")
                except:
                    pass
                
        browser.close()

if __name__ == "__main__":
    find_links()
