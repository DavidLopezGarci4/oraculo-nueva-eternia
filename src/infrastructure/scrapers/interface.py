from typing import List, Protocol, Dict, Any
from src.infrastructure.scrapers.base import ScrapedOffer

# Alias para compatibilidad regresiva
ProductOffer = ScrapedOffer

class ScraperPlugin(Protocol):
    """Protocol that all store scrapers must implement."""
    
    def search(self, query: str) -> List[ScrapedOffer]:
        """
        Search for products based on a query string.
        Should return a clean list of ScrapedOffer or empty list on error.
        """
        ...
    
    @property
    def name(self) -> str:
        """Name of the store (e.g. 'ActionToys')."""
        ...
    
    @property
    def is_active(self) -> bool:
        """Feature flag to enable/disable scraper."""
        ...

