import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Testing Playwright with Chrome Channel, Homepage landing, and advanced Stealth...")
    async with async_playwright() as p:
        try:
            # Try launching with real Chrome channel first
            print("Launching Chrome channel...")
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
        except Exception as e:
            print(f"Failed to launch Chrome channel ({e}). Falling back to standard Chromium...")
            browser = await p.chromium.launch(
                headless=True,
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
        
        # Advanced injections
        await page.add_init_script("""
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['de-DE', 'de', 'en-US', 'en']
            });
            const mockPlugin = (name, filename, description) => {
                const plugin = Object.create(Plugin.prototype);
                Object.defineProperties(plugin, {
                    name: { value: name, enumerable: true },
                    filename: { value: filename, enumerable: true },
                    description: { value: description, enumerable: true },
                });
                return plugin;
            };
            const pluginsList = [
                mockPlugin('PDF Viewer', 'internal-pdf-viewer', 'Portable Document Format'),
                mockPlugin('Chrome PDF Viewer', 'mhjfbgojcjbhgoocpbhnapeenohidgkm', 'Portable Document Format')
            ];
            Object.defineProperty(navigator, 'plugins', {
                get: () => pluginsList,
                enumerable: true,
                configurable: true
            });
        """)
        
        try:
            # Visit homepage first to set cookies
            print("Step 1: Visiting homepage...")
            await page.goto("https://www.smythstoys.com/de/de-de", wait_until="load", timeout=30000)
            await asyncio.sleep(random.uniform(2.5, 4.5))
            
            # Navigate to category page
            print("Step 2: Navigating to category page...")
            await page.goto(URL, wait_until="load", timeout=60000)
            await asyncio.sleep(random.uniform(3.0, 5.0))
            
            # Simulate human scrolls
            print("Step 3: Simulating human scrolls...")
            for i in range(3):
                scroll_y = random.randint(300, 600)
                await page.mouse.wheel(0, scroll_y)
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower():
                print("[BLOCKED] WAF blockade still active.")
                # Save block page
                with open("scratch/smyths_blocked_hybrid.html", "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                print("[OK] Success! Bypassed Imperva!")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links!")
                for idx, pl in enumerate(p_links[:5]):
                    print(f"  {idx}: '{pl.get_text(strip=True)[:40]}' -> {pl['href']}")
                    
                with open("scratch/smyths_success_hybrid.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
