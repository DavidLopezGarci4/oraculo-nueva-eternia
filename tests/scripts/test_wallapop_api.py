import asyncio
from curl_cffi.requests import AsyncSession

async def run():
    url = "https://es.wallapop.com/search?keywords=masters%20of%20the%20universe%20origins&order_by=newest"
    session = AsyncSession(impersonate="chrome120")
    resp = await session.get(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
    })
    
    with open("tests/scripts/wallapop.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"Status: {resp.status_code}, Saved to tests/scripts/wallapop.html")

asyncio.run(run())
