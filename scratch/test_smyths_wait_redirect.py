import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Starting WAF solver test (emoji-free, detailed log)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            channel="chrome",
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
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
            print("Step 1: Navigating to homepage...")
            await page.goto("https://www.smythstoys.com/de/de-de", wait_until="commit")
            
            # Wait to see if challenge solves itself
            print("Waiting for page title to change or settle on homepage...")
            for i in range(30):
                await asyncio.sleep(1)
                try:
                    title = await page.title()
                    url = page.url
                    print(f"  [{i+1}s] Title: '{title}', URL: {url}")
                    if title and "Pardon Our Interruption" not in title and "interruption" not in title.lower():
                        print("[OK] Homepage WAF solved!")
                        break
                except Exception as e:
                    print(f"  [{i+1}s] Context destroyed / redirecting... ({e})")
            
            # Print cookies
            cookies = await context.cookies()
            print(f"Cookies after homepage: {len(cookies)}")
            for c in cookies:
                if "incap" in c["name"] or "reese" in c["name"]:
                    print(f"  Cookie: {c['name']} = {c['value'][:20]}...")
            
            # Navigate to category page
            print("Step 2: Navigating to category page...")
            await page.goto(URL, wait_until="commit")
            
            print("Waiting for category page to settle...")
            for i in range(15):
                await asyncio.sleep(1)
                try:
                    title = await page.title()
                    url = page.url
                    print(f"  [{i+1}s] Title: '{title}', URL: {url}")
                    if "Pardon Our Interruption" not in title and "interruption" not in title.lower():
                        print("[OK] Category page WAF solved!")
                        break
                except Exception as e:
                    print(f"  [{i+1}s] Context destroyed / redirecting... ({e})")
                    
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            # Save HTML for analysis
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower():
                print("[BLOCKED] Blocked on category page.")
                with open("scratch/smyths_blocked_redirect.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("Saved scratch/smyths_blocked_redirect.html")
            else:
                print("[SUCCESS] Bypassed successfully!")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links.")
                for idx, pl in enumerate(p_links[:5]):
                    print(f"  {idx}: {pl.get_text(strip=True)[:40]} -> {pl['href']}")
                with open("scratch/smyths_success_redirect.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("Saved scratch/smyths_success_redirect.html")
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
