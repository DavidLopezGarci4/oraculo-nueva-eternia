from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import LogisticRuleModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_logistics(db_session=None):
    """
    Puebla y sincroniza la tabla logistic_rules con las tarifas comerciales aprobadas.
    """
    rules = [
        # Tiendas Nacionales (España - Destino ES)
        {"shop_name": "Amazon.es", "country_code": "ES", "base_shipping": 0.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "ToymiEU", "country_code": "ES", "base_shipping": 5.50, "free_shipping_threshold": 75.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Frikimaz", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 69.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Triguetech", "country_code": "ES", "base_shipping": 7.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": "triguetech_flat_rate"},
        {"shop_name": "DVDStoreSpain", "country_code": "ES", "base_shipping": 4.50, "free_shipping_threshold": 50.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Electropolis", "country_code": "ES", "base_shipping": 6.50, "free_shipping_threshold": 150.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Fantasia Personajes", "country_code": "ES", "base_shipping": 5.89, "free_shipping_threshold": 60.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Frikiverso", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 80.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Pixelatoy", "country_code": "ES", "base_shipping": 6.00, "free_shipping_threshold": 100.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "LaMansionDelTerror", "country_code": "ES", "base_shipping": 4.90, "free_shipping_threshold": 70.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Tradeinn", "country_code": "ES", "base_shipping": 2.99, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},

        # Plataformas de Segunda Mano / Marketplaces P2P (Envío 5€ + 2% Seguro sobre ítem)
        {"shop_name": "Ebay.es", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.02, "custom_fees": 0.0, "strategy_key": "p2p_insurance"},
        {"shop_name": "Vinted", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.02, "custom_fees": 0.0, "strategy_key": "p2p_insurance"},
        {"shop_name": "Wallapop", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.02, "custom_fees": 0.0, "strategy_key": "p2p_insurance"},

        # USA (Gran Importación - 8.00$ envío base + 21% IVA)
        {"shop_name": "BigBadToyStore", "country_code": "ES", "base_shipping": 8.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.21, "custom_fees": 0.0, "strategy_key": "bbts_flat_rate"},

        # Tiendas Europeas (Importación UE)
        {"shop_name": "SmythsToys", "country_code": "ES", "base_shipping": 4.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.00, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "DeToyboys", "country_code": "ES", "base_shipping": 15.00, "free_shipping_threshold": 200.0, "vat_multiplier": 1.05, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Time4ActionToysDE", "country_code": "ES", "base_shipping": 18.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "MotuClassicsDE", "country_code": "ES", "base_shipping": 18.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "VendiloshopIT", "country_code": "ES", "base_shipping": 12.00, "free_shipping_threshold": 150.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
    ]

    deprecated_shops = ["ActionToys", "Toymi", "Fantasia"]

    def _execute(db):
        for dep_shop in deprecated_shops:
            db.query(LogisticRuleModel).filter(LogisticRuleModel.shop_name == dep_shop).delete()

        for rule_data in rules:
            rule = db.query(LogisticRuleModel).filter(
                LogisticRuleModel.shop_name == rule_data["shop_name"],
                LogisticRuleModel.country_code == rule_data["country_code"]
            ).first()
            
            if rule:
                for key, value in rule_data.items():
                    setattr(rule, key, value)
            else:
                rule = LogisticRuleModel(**rule_data)
                db.add(rule)
        
        db.commit()

    if db_session:
        _execute(db_session)
    else:
        with SessionCloud() as db:
            _execute(db)
    logger.info("Seed de Oráculo Logístico actualizado con éxito.")

if __name__ == "__main__":
    seed_logistics()
