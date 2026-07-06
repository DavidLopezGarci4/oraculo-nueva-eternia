import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Testing Playwright with Stealth configuration...")
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
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--window-size=1920,1080',
                '--start-maximized',
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            screen={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            locale='de-DE',
            timezone_id='Europe/Berlin',
            color_scheme='light',
            has_touch=False,
            is_mobile=False,
        )
        
        await context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cache-Control': 'max-age=0',
        })
        
        page = await context.new_page()
        
        # We can also add webdriver bypass injection
        await page.add_init_script("delete navigator.__proto__.webdriver")
        
        try:
            print(f"Navigating to {URL}...")
            resp = await page.goto(URL, wait_until="networkidle", timeout=60000)
            print(f"Status: {resp.status if resp else 'None'}")
            
            # Wait for content to hydrate
            await asyncio.sleep(5)
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "imperva" in body_text.lower():
                print("[BLOCKED] Blocked by Imperva WAF even with Stealth Playwright!")
                print(body_text[:500].strip())
            else:
                print("[OK] Stealth Playwright bypassed Imperva!")
                # Let's search for '/p/' links (product links)
                p_links = soup.select("a[href*='/p/']")
                print(f"Found {len(p_links)} links containing '/p/'")
                for idx, pl in enumerate(p_links[:10]):
                    print(f"  - {idx}: '{pl.get_text(strip=True)}' -> {pl.get('href')}")
                    
                # Write page source to verify product list
                with open("scratch/smyths_stealth.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("Saved scratch/smyths_stealth.html")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
