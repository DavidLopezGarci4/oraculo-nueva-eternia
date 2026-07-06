import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Testing Playwright in HEADED mode (headless=False) to get real HTML...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--window-size=1280,720',
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720},
            locale='de-DE',
            timezone_id='Europe/Berlin',
        )
        
        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver")
        
        try:
            print(f"Navigating to {URL}...")
            await page.goto(URL, wait_until="load", timeout=60000)
            
            print("Please solve any captcha or verify page if it appears. Waiting 15 seconds...")
            await asyncio.sleep(15)
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "imperva" in body_text.lower():
                print("[ERROR] Still blocked in headed mode!")
            else:
                print("[SUCCESS] Bypassed WAF in headed mode!")
                # Find some elements
                # Let's see if we can find any class names that look like product cards
                # E.g., cards usually have class containing "product", "grid", "card", or "tile"
                cards = soup.select("[class*='product'], [class*='card'], [class*='tile']")
                print(f"Total element count with card/product/tile in class: {len(cards)}")
                
                # Write HTML to file
                with open("scratch/smyths_headed_success.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("Saved scratch/smyths_headed_success.html")
                
                # Check for /p/ links
                links = soup.find_all("a", href=True)
                print(f"Total links: {len(links)}")
                p_links = [l for l in links if "/p/" in l["href"] or "/c/" in l["href"]]
                print(f"Sample links found:")
                for l in p_links[:20]:
                    print(f"  - '{l.get_text(strip=True)[:40]}' -> {l['href']}")
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
