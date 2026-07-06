import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import tempfile
import shutil

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Testing clean native Playwright without JS monkey-patching...")
    user_data_dir = tempfile.mkdtemp(prefix="playwright_test_")
    
    async with async_playwright() as p:
        try:
            # Launch persistent context
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ],
                viewport={'width': 1366, 'height': 768},
                locale='de-DE',
                timezone_id='Europe/Berlin',
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Step 1: Visit homepage
            print("Step 1: Visiting homepage...")
            await page.goto("https://www.smythstoys.com/de/de-de", wait_until="commit", timeout=45000)
            await asyncio.sleep(5)
            
            title = await page.title()
            print(f"Homepage Title: '{title}'")
            
            # Step 2: Navigate to category with referer
            print("Step 2: Navigating to category page...")
            await page.goto(URL, referer="https://www.smythstoys.com/de/de-de", wait_until="commit", timeout=45000)
            await asyncio.sleep(5)
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower() or "incident id" in html.lower():
                print("Result: BLOCKED")
            else:
                print("Result: SUCCESS!")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await context.close()
            try:
                shutil.rmtree(user_data_dir)
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())
