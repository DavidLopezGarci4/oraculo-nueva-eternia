import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

async def main():
    print("Testing real browser search flow to bypass WAF...")
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
            viewport={'width': 1366, 'height': 768},
            locale='de-DE',
            timezone_id='Europe/Berlin',
        )
        
        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver")
        
        try:
            print("Step 1: Navigating to homepage...")
            await page.goto("https://www.smythstoys.com/de/de-de", wait_until="load", timeout=45000)
            await asyncio.sleep(random.uniform(3.0, 5.0))
            
            title = await page.title()
            print(f"Homepage Title: '{title}', URL: {page.url}")
            
            if "Pardon Our Interruption" in title:
                print("Homepage blocked by WAF. Waiting 10s to see if it solves...")
                await asyncio.sleep(10)
                title = await page.title()
                print(f"After wait - Title: '{title}'")
                if "Pardon Our Interruption" in title:
                    print("Could not bypass homepage WAF.")
                    return
            
            # Step 2: Locating the search input field
            print("Step 2: Locating search input...")
            search_selectors = [
                "input[placeholder*='Suche']",
                "input[type='text']",
                ".headerSearchForm input"
            ]
            
            search_input = None
            for sel in search_selectors:
                try:
                    el = await page.wait_for_selector(sel, timeout=5000)
                    if el:
                        search_input = el
                        print(f"  Found search input using selector: '{sel}'")
                        break
                except Exception:
                    continue
                    
            if not search_input:
                print("Could not locate search input field on the page.")
                # Save page to inspect
                html = await page.content()
                with open("scratch/smyths_homepage_no_input.html", "w", encoding="utf-8") as f:
                    f.write(html)
                return
                
            # Click and type like a human
            print("Step 3: Clicking and typing query...")
            await search_input.click()
            await asyncio.sleep(random.uniform(0.5, 1.2))
            
            # Type motu
            query = "masters of the universe"
            for char in query:
                await search_input.type(char, delay=random.randint(80, 200))
                
            await asyncio.sleep(random.uniform(0.8, 1.5))
            
            print("Step 4: Pressing Enter to search...")
            # We can press Enter or click the search button
            await search_input.press("Enter")
            
            print("Waiting for search results navigation...")
            await asyncio.sleep(random.uniform(5.0, 8.0))
            
            # Check results
            title = await page.title()
            url = page.url
            print(f"Results Page Title: '{title}', URL: {url}")
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower():
                print("WAF Blocked the search results page.")
                with open("scratch/smyths_search_blocked.html", "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                print("SUCCESS! Search results loaded without WAF blockade!")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links.")
                for idx, pl in enumerate(p_links[:10]):
                    print(f"  {idx}: {pl.get_text(strip=True)[:40]} -> {pl['href']}")
                with open("scratch/smyths_search_success.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
        except Exception as e:
            print(f"Error during execution: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
