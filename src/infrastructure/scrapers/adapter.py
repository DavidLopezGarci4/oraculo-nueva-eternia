import hashlib
from datetime import datetime
from typing import List, Optional
from src.infrastructure.scrapers.base import ScrapedOffer as LegacyOffer
from loguru import logger

class Scraper3OXAdapter:
    """
    Adaptador de Grado Industrial 3OX para Scrapers.
    Convierte ofertas 'Legacy' en objetos que cumplen el contrato dev/contract.ref
    y genera recibos de auditoría criptográficos.
    """

    @staticmethod
    def generate_receipt(shop_name: str, url: str, price: float) -> str:
        """Genera un ID único e inmutable para la captura."""
        data = f"{shop_name}|{url}|{price:.2f}"
        return hashlib.sha256(data.encode()).hexdigest()[:16] # Usamos SHA256[16] por compatibilidad

    @classmethod
    def transform(cls, legacy_offers: List[LegacyOffer]) -> List[dict]:
        """Transforma una lista de ofertas al formato de contrato 3OX."""
        transformed = []
        for offer in legacy_offers:
            try:
                receipt = cls.generate_receipt(offer.shop_name, offer.url, offer.price)
                
                transformed_item = {
                    "product_name": offer.product_name,
                    "price": round(offer.price, 2),
                    "currency": offer.currency,
                    "url": offer.url,
                    "shop_name": offer.shop_name,
                    "is_available": offer.is_available,
                    "ean": offer.ean,
                    "image_url": offer.image_url,
                    "scraped_at": offer.scraped_at.isoformat(),
                    "receipt_id": receipt,
                    # Phase 3OX.Auction :: Preservación de Metadatos de Subasta
                    "source_type": offer.source_type,
                    "sale_type": offer.sale_type,
                    "expiry_at": offer.expiry_at.isoformat() if offer.expiry_at else None,
                    "bids_count": offer.bids_count,
                    "time_left_raw": offer.time_left_raw,
                    "first_seen_at": offer.first_seen_at.isoformat() if offer.first_seen_at else None,
                    "sold_at": offer.sold_at.isoformat() if offer.sold_at else None,
                    "is_sold": offer.is_sold,
                    "shipping_price": offer.shipping_price
                }
                transformed.append(transformed_item)
            except Exception as e:
                logger.error(f"Error transformando oferta {offer.product_name}: {e}")
        
        return transformed

# Singleton para uso global
adapter = Scraper3OXAdapter()
