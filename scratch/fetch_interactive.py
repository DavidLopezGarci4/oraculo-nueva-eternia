import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Starting headed browser for interactive solve...")
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
            
            print("Please solve the WAF captcha in the opened browser window if needed.")
            print("The script will automatically detect when the page is loaded and close.")
            
            solved = False
            for sec in range(120):
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                body_text = soup.body.get_text() if soup.body else ""
                
                # Check if we have the real product grid
                # Real products on Smyths usually contain links like /de/de-de/... or /p/
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"] or "/c/" in l["href"]]
                
                # If we have many links and no WAF block text
                if len(links) > 20 and "incapsula" not in html.lower() and "pardon our interruption" not in body_text.lower():
                    print(f"Success! Page loaded. Total links found: {len(links)}")
                    with open("scratch/smyths_solved_success.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    print("Saved HTML to scratch/smyths_solved_success.html")
                    solved = True
                    break
                    
                if sec % 5 == 0:
                    print(f"  [{sec}s] Waiting... (Links: {len(links)}, Blocked: {'yes' if 'incapsula' in html.lower() else 'no'})")
                await asyncio.sleep(1)
                
            if not solved:
                print("Timeout reached without successful bypass.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
