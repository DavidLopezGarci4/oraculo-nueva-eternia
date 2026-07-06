import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import tempfile
import shutil

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Running advanced automated stealth check...")
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
                viewport={'width': 1280, 'height': 720},
                locale='de-DE',
                timezone_id='Europe/Berlin',
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            
            # 1. Retrieve the native user agent and clean it
            raw_ua = await page.evaluate("navigator.userAgent")
            clean_ua = raw_ua.replace("HeadlessChrome/", "Chrome/")
            print(f"Original UA: {raw_ua}")
            print(f"Cleaned UA:  {clean_ua}")
            
            # Set extra headers matching the cleaned UA
            await context.set_extra_http_headers({
                'User-Agent': clean_ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            })
            
            # Inject advanced antidetect overrides
            await page.add_init_script("delete navigator.__proto__.webdriver")
            
            # Use non-f-string interpolation to avoid brackets issues
            js_script = """
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => 'CLEAN_UA_PLACEHOLDER'
                });
                
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['de-DE', 'de', 'en-US', 'en']
                });
            """.replace("CLEAN_UA_PLACEHOLDER", clean_ua)
            
            await page.add_init_script(js_script)
            
            # Step 1: Visit homepage
            print("Step 1: Visiting homepage...")
            await page.goto("https://www.smythstoys.com/de/de-de", wait_until="commit", timeout=45000)
            await asyncio.sleep(5)
            
            # Step 2: Navigate to category with referer
            print("Step 2: Navigating to category page...")
            await page.goto(URL, referer="https://www.smythstoys.com/de/de-de", wait_until="commit", timeout=45000)
            await asyncio.sleep(5)
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower() or "incident id" in html.lower():
                print("Result: BLOCKED")
                with open("scratch/smyths_blocked_clean_ua.html", "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                print("Result: SUCCESS")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links.")
                with open("scratch/smyths_success_clean_ua.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
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
