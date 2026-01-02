from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        # Launch browser (headless=False so user can see it working)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Navigating to Fantasia Personajes...")
        page.goto("https://fantasiapersonajes.es/buscar?controller=search&s=masters+of+the+universe+origins")
        
        # Wait for initial load
        page.wait_for_timeout(5000)
        
        # Scroll down to trigger infinite scroll / dynamic loading
        print("Scrolling down...")
        for i in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            
        # Count items
        items = page.locator(".product-miniature, .js-product-miniature, .product_list_item").all()
        print(f"Found {len(items)} items on the page.")
        
        # Extract titles to verify variety
        print("--- Sample Items ---")
        for i, item in enumerate(items[:5]):
            print(f"{i+1}. {item.inner_text().splitlines()[0]}")
            
        browser.close()

if __name__ == "__main__":
    run()
