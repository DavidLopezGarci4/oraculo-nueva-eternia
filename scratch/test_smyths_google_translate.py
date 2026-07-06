import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
import urllib.parse

# Category URL
URL = "https://www.smythstoys.com/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe-figuren-und-sets/c/SM1001010408?sort=creationDate_dt%20desc"

async def main():
    print("Testing WAF bypass using Google Translate proxy...")
    
    # URL format for Google Translate translation page
    encoded_url = urllib.parse.quote(URL, safe="")
    translate_url = f"https://translate.google.com/translate?sl=de&tl=en&u={encoded_url}"
    
    print(f"Translate URL: {translate_url}")
    
    try:
        async with AsyncSession() as session:
            # We can use impersonate="chrome120" to look like a browser
            resp = await session.get(translate_url, impersonate="chrome120", timeout=30)
            print(f"Response status: {resp.status_code}")
            
            # Let's inspect the title and links
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string if soup.title else "None"
            print(f"Title: {title}")
            
            # Check if there are iframes or links containing googletranslate
            iframe = soup.find("iframe", {"name": "c"}) or soup.find("iframe")
            if iframe:
                print(f"Found translation iframe src: {iframe.get('src')}")
                
            # Let's save the HTML to inspect
            with open("scratch/smyths_translate.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("Saved HTML to scratch/smyths_translate.html")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
