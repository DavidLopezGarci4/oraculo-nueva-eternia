
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import LogisticRuleModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_spanish_rules():
    rules = [
        # Tradeinn: Volume strategy
        {
            "shop_name": "Tradeinn",
            "country_code": "ES",
            "base_shipping": 2.99,
            "free_shipping_threshold": 0.0,
            "vat_multiplier": 1.0, # Precios en ES suelen incluir IVA, pero aquí definimos el factor de ajuste si fuera necesario
            "custom_fees": 0.0,
            "strategy_key": "tradeinn_volume"
        },
        # Electropolis: Free shipping > 100
        {
            "shop_name": "Electropolis",
            "country_code": "ES",
            "base_shipping": 3.49,
            "free_shipping_threshold": 100.0,
            "vat_multiplier": 1.0,
            "custom_fees": 0.0,
            "strategy_key": None
        },
        # DVDStoreSpain: Free shipping > 60
        {
            "shop_name": "DVDStoreSpain",
            "country_code": "ES",
            "base_shipping": 4.75,
            "free_shipping_threshold": 60.0,
            "vat_multiplier": 1.0,
            "custom_fees": 0.0,
            "strategy_key": None
        },
        # Fantasia Personajes: 4.89 flat rate (updated from HTML)
        {
            "shop_name": "Fantasia Personajes",
            "country_code": "ES",
            "base_shipping": 4.89,
            "free_shipping_threshold": 0.0,
            "vat_multiplier": 1.0,
            "custom_fees": 0.0,
            "strategy_key": None
        },
        # Frikiverso: Free shipping > 60
        {
            "shop_name": "Frikiverso",
            "country_code": "ES",
            "base_shipping": 4.75,
            "free_shipping_threshold": 60.0,
            "vat_multiplier": 1.0,
            "custom_fees": 0.0,
            "strategy_key": None
        },
        # Pixelatoy: 4.95 flat rate
        {
            "shop_name": "Pixelatoy",
            "country_code": "ES",
            "base_shipping": 4.95,
            "free_shipping_threshold": 0.0,
            "vat_multiplier": 1.0,
            "custom_fees": 0.0,
            "strategy_key": None
        }
    ]

    with SessionCloud() as db:
        for r_data in rules:
            existing = db.query(LogisticRuleModel).filter(
                LogisticRuleModel.shop_name == r_data["shop_name"],
                LogisticRuleModel.country_code == r_data["country_code"]
            ).first()

            if existing:
                logger.info(f"Updating rule for {r_data['shop_name']}")
                for key, value in r_data.items():
                    setattr(existing, key, value)
            else:
                logger.info(f"Creating new rule for {r_data['shop_name']}")
                new_rule = LogisticRuleModel(**r_data)
                db.add(new_rule)
        
        db.commit()
        logger.info("Successfully populated Spanish logistic rules.")

if __name__ == "__main__":
    populate_spanish_rules()
