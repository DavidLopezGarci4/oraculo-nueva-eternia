import asyncio
from curl_cffi.requests import AsyncSession

async def main():
    print("Fetching Smyths Toys robots.txt...")
    url = "https://www.smythstoys.com/robots.txt"
    try:
        async with AsyncSession() as session:
            resp = await session.get(url, impersonate="chrome120", timeout=30)
            print(f"Status: {resp.status_code}")
            print("Content:")
            print(resp.text[:2000])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
