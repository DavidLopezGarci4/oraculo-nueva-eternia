
import random
import logging
from curl_cffi.requests import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class WallapopBridge:
    """
    Bridge service to interact with Wallapop internal API for detailed item inspection.
    Bypasses 403 blocks using curl-cffi impersonation.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]

    @classmethod
    def _get_headers(cls) -> dict:
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Origin": "https://es.wallapop.com",
            "Referer": "https://es.wallapop.com/",
        }

    @classmethod
    async def get_item_details(cls, item_url: str) -> Optional[Dict[str, Any]]:
        """
        Extracts item ID from URL and fetches full details from Wallapop API.
        """
        # 1. Extract ID from Slug (e.g. .../item/figura-motu-123456789)
        try:
            item_slug = item_url.split("/item/")[-1].split("?")[0]
            # If slug contains the ID at the end or is just the ID
            # Wallapop slugs usually end with ID or are ID themselves
            # Example: https://es.wallapop.com/item/battle-cat-motu-origins-987654321
            item_id = item_slug.split("-")[-1] if "-" in item_slug else item_slug
        except Exception as e:
            logger.error(f"Failed to extract Wallapop ID: {e}")
            return None

        api_url = f"https://api.wallapop.com/api/v3/items/{item_id}"
        
        try:
            async with AsyncSession() as session:
                response = await session.get(
                    api_url,
                    headers=cls._get_headers(),
                    impersonate="chrome120",
                    timeout=20
                )
                
                if response.status_code != 200:
                    logger.error(f"Wallapop API (v3/items) failed: {response.status_code}")
                    return None
                
                data = response.json()
                
                # Normalize response for Frontend
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "price": data.get("price", {}).get("amount"),
                    "currency": data.get("price", {}).get("currency"),
                    "images": [img.get("original") for img in data.get("images", [])],
                    "seller": {
                        "name": data.get("user", {}).get("micro_name"),
                        "stats": data.get("user", {}).get("stats", {}),
                        "avatar": data.get("user", {}).get("image", {}).get("original")
                    },
                    "location": data.get("location", {}).get("city"),
                    "published_at": data.get("modification_date"), # Approx listing date
                    "url": item_url
                }
        except Exception as e:
            logger.error(f"Wallapop Bridge Error: {e}")
            return None
