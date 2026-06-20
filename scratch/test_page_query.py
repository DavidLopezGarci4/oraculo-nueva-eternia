import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

async def main():
    url = "https://lamansiondelterror.es/es/busqueda?q=wwe+masters+tmnt+of+the+universe+origins&page=3"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    async with AsyncSession() as session:
        resp = await session.get(url, headers=headers, impersonate="chrome120", timeout=30)
        print("Page 3 Query Status Code:", resp.status_code)
        
        soup = BeautifulSoup(resp.text, "html.parser")
        products = soup.select(".product")
        print(f"Page 3 Query found {len(products)} products.")
        
        if products:
            title_a = products[0].select_one("h3.text-3-5 a")
            name = title_a.get_text(strip=True) if title_a else "No name"
            print("First product on page 3:", name)

if __name__ == "__main__":
    asyncio.run(main())
