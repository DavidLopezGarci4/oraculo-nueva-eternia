from src.infrastructure.scrapers.base import ScrapedOffer
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from loguru import logger

def test_conversion():
    offer = ScrapedOffer(
        product_name="Test Product",
        price=10.0,
        url="http://example.com",
        shop_name="Test Shop"
    )
    
    offers = [offer]
    
    print(f"Offer type: {type(offers[0])}")
    print(f"Has model_dump: {hasattr(offers[0], 'model_dump')}")
    print(f"Has dict: {hasattr(offers[0], 'dict')}")
    
    # Simulate pipeline logic
    if hasattr(offers[0], 'model_dump'):
        print("Converting with model_dump")
        offers = [o.model_dump() for o in offers]
    elif hasattr(offers[0], 'dict'):
        print("Converting with dict")
        offers = [o.dict() for o in offers]
        
    print(f"Final offer type: {type(offers[0])}")
    try:
        print(f"Shop name via get: {offers[0].get('shop_name')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_conversion()
