import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

URL = "https://www-smythstoys-com.translate.goog/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt+desc&_x_tr_sl=de&_x_tr_tl=en"

async def main():
    print("Testing direct Google Translate mirror domain fetch...")
    try:
        async with AsyncSession() as session:
            resp = await session.get(URL, impersonate="chrome120", timeout=30)
            print(f"Response status: {resp.status_code}")
            
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")
            body_text = soup.body.get_text() if soup.body else ""
            
            print(f"Title: {soup.title.string if soup.title else 'None'}")
            
            if "pardon our interruption" in body_text.lower() or "incapsula" in html.lower():
                print("Result: BLOCKED (Imperva blocked Google Translate crawler)")
                with open("scratch/smyths_translate_goog_blocked.html", "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                print("Result: SUCCESS!")
                links = soup.find_all("a", href=True)
                p_links = [l for l in links if "/p/" in l["href"]]
                print(f"Found {len(p_links)} product links.")
                for idx, pl in enumerate(p_links[:5]):
                    print(f"  {idx}: {pl.get_text(strip=True)[:40]} -> {pl['href']}")
                with open("scratch/smyths_translate_goog_success.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
