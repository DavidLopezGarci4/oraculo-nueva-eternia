import asyncio
from curl_cffi.requests import AsyncSession

async def main():
    url = "https://lamansiondelterror.es/es/busqueda?q=wwe"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    async with AsyncSession() as session:
        resp = await session.get(url, headers=headers, impersonate="chrome120", timeout=30)
        print("Simple Query Status Code:", resp.status_code)
        print("Simple Query HTML length:", len(resp.text))
        
        # Check if we can find any products
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        products = soup.select(".product")
        print(f"Simple Query found {len(products)} products.")

if __name__ == "__main__":
    asyncio.run(main())
