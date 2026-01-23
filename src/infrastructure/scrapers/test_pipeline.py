import asyncio
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from loguru import logger

async def test_pipeline():
    logger.info("Initializing Scrapers...")
    amazon = AmazonScraper()
    
    pipeline = ScrapingPipeline(scrapers=[amazon])
    
    # Test with a known MOTU product
    product_name = "He-Man Masterverse"
    logger.info(f"Testing pipeline for: {product_name}")
    
    offers = await pipeline.run_product_search(product_name)
    
    logger.success(f"Pipeline finished. Found {len(offers)} offers.")
    for offer in offers:
        logger.info(f"[{offer.shop_name}] {offer.product_name} - {offer.price}€ - {offer.url}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
