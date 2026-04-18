import asyncio
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.infrastructure.scrapers.base import BaseScraper

class MockScraper(BaseScraper):
    async def search(self, query: str): return []

async def test_amazon():
    scraper = MockScraper("AmazonDebug")
    # Use a standard MOTU query
    url = "https://www.amazon.es/s?k=masters+of+the+universe+origins"
    html = await scraper._curl_get(url)
    if html:
        print(f"Success! HTML length: {len(html)}")
        with open("amazon_diagnostic.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML saved to amazon_diagnostic.html")
        
        # Check if results are present in HTML
        if "[data-component-type='s-search-result']" in html:
            print("Selector [data-component-type='s-search-result'] FOUND in raw HTML")
        else:
            print("Selector [data-component-type='s-search-result'] NOT FOUND in raw HTML")
            # Look for common markers
            if "s-result-item" in html:
                print("Marker 's-result-item' FOUND")
            if "captcha" in html.lower():
                print("CAPTCHA detected in HTML")
            if "robot" in html.lower():
                print("ROBOT detected in HTML")
    else:
        print("Failed to get HTML from Amazon")

if __name__ == "__main__":
    asyncio.run(test_amazon())
