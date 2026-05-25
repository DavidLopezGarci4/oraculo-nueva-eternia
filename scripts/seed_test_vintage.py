from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_test_vintage")

def seed_vintage_items():
    logger.info("Iniciando el sembrado de reliquias vintage de prueba...")
    
    test_items = [
        {
            "scraped_name": "He-Man Vintage 1982 completo",
            "ean": None,
            "price": 45.0,
            "currency": "EUR",
            "url": "https://es.wallapop.com/item/he-man-vintage-1982-completo-fictional-1",
            "shop_name": "Wallapop",
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/he-man-motu-original.jpg",
            "source_type": "Peer-to-Peer",
            "is_vintage": True,
            "condition": "Loose",
            "grading": 7.5
        },
        {
            "scraped_name": "Skeletor vintage 1982 en blister",
            "ean": None,
            "price": 180.0,
            "currency": "EUR",
            "url": "https://www.ebay.es/itm/skeletor-vintage-1982-in-blister-fictional-2",
            "shop_name": "eBay",
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/skeletor-motu-original.jpg",
            "source_type": "Peer-to-Peer",
            "is_vintage": True,
            "condition": "MOC",
            "grading": 8.5
        },
        {
            "scraped_name": "He-Man 1984 Loose",
            "ean": None,
            "price": 35.0,
            "currency": "EUR",
            "url": "https://www.vinted.es/items/he-man-1984-loose-fictional-3",
            "shop_name": "Vinted",
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/he-man-motu-original.jpg",
            "source_type": "Peer-to-Peer",
            "is_vintage": True,
            "condition": "Loose",
            "grading": 6.5
        },
        {
            "scraped_name": "Man-At-Arms Vintage 1983 figura",
            "ean": None,
            "price": 50.0,
            "currency": "EUR",
            "url": "https://es.wallapop.com/item/man-at-arms-vintage-1983-fictional-4",
            "shop_name": "Wallapop",
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/man-at-arms-original.jpg",
            "source_type": "Peer-to-Peer",
            "is_vintage": True,
            "condition": "Loose",
            "grading": 8.0
        }
    ]
    
    with SessionCloud() as db:
        for item_data in test_items:
            # Eliminar si ya existe la URL para evitar errores de restricción unique
            db.query(PendingMatchModel).filter(PendingMatchModel.url == item_data["url"]).delete()
            
            pending = PendingMatchModel(
                scraped_name=item_data["scraped_name"],
                ean=item_data["ean"],
                price=item_data["price"],
                currency=item_data["currency"],
                url=item_data["url"],
                shop_name=item_data["shop_name"],
                image_url=item_data["image_url"],
                source_type=item_data["source_type"],
                is_vintage=item_data["is_vintage"],
                condition=item_data["condition"],
                grading=item_data["grading"],
                found_at=datetime.now(timezone.utc)
            )
            db.add(pending)
        
        db.commit()
        logger.info("¡Sembrado de reliquias completado con éxito!")

if __name__ == "__main__":
    seed_vintage_items()
