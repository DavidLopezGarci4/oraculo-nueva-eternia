import asyncio
from playwright.async_api import async_playwright

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale='de-DE',
            timezone_id='Europe/Berlin',
        )
        
        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver")
        
        try:
            print("Navigating...")
            await page.goto(URL, wait_until="commit", timeout=60000)
            
            # Wait for 15 seconds to let Incapsula challenge run
            print("Waiting for challenge execution...")
            for i in range(15):
                await asyncio.sleep(1)
                title = await page.title()
                url = page.url
                print(f"  Sec {i+1} - Title: '{title}', URL: {url}")
                
            html = await page.content()
            if "incapsula" in html.lower():
                print("❌ Still blocked by Incapsula/Imperva.")
            else:
                print("✅ Challenge solved! We have the real page!")
                with open("scratch/smyths_solved.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
