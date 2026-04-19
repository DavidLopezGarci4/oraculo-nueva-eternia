import asyncio
import sys
import os
import re
from bs4 import BeautifulSoup

# Add src to path
sys.path.append(os.getcwd())

from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.infrastructure.scrapers.base import ScrapedOffer

async def test_amazon_extraction():
    scraper = AmazonScraper()
    # Read the previously saved HTML
    if not os.path.exists("amazon_diagnostic.html"):
        print("amazon_diagnostic.html not found. Run previous diagnostic first.")
        return

    with open("amazon_diagnostic.html", "r", encoding="utf-8") as f:
        html = f.read()

    print(f"Analyzing saved HTML ({len(html)} bytes)...")
    
    # Use the real search logic (refactored to take HTML directly for testing)
    # Since search() normally fetches HTML, I'll simulate the extraction part
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Detect block
    if "captcha" in html.lower() or "robot" in html.lower():
        print("🚫 Block detected in HTML (captcha/robot keywords found)")

    # Extract results - Mirroring the new AmazonScraper logic
    results = soup.select("[data-asin]")
    if not results:
        results = soup.select(".s-result-item")
    
    print(f"📊 Detectados {len(results)} bloques con [data-asin]/.s-result-item.")

    offers = []
    for res in results:
        asin = res.get("data-asin")
        if not asin or len(asin) != 10:
            continue

        try:
            # Title
            title = "Unknown"
            title_el = (
                res.select_one("h2 a span") or 
                res.select_one(".a-size-medium.a-color-base.a-text-normal") or
                res.select_one(".a-size-base-plus.a-color-base.a-text-normal") or
                res.select_one("h2")
            )
            if title_el:
                title = title_el.get_text(strip=True)
            
            # Price
            price_text = "N/A"
            price = 0.0
            price_el = (
                res.select_one(".a-price .a-offscreen") or
                res.select_one(".a-price-whole") or
                res.select_one(".a-color-price")
            )
            if price_el:
                price_text = price_el.get_text()
                price = scraper._normalize_price(price_text)

            if price > 0:
                offers.append({
                    "title": title,
                    "price": price,
                    "asin": asin
                })
        except Exception as e:
            print(f"Error in extraction: {e}")

    print(f"✅ Success! Extracted {len(offers)} offers.")
    for o in offers[:5]:
        print(f" - [{o['asin']}] {o['title'][:40]}... -> {o['price']}€")

if __name__ == "__main__":
    asyncio.run(test_amazon_extraction())
