from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import LogisticRuleModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_logistics():
    """
    Puebla la tabla logistic_rules con datos iniciales para Phase 15.
    """
    rules = [
        # Tiendas Españolas (Destino ES)
        {"shop_name": "Fantasia Personajes", "country_code": "ES", "base_shipping": 5.89, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "ToymiEU", "country_code": "ES", "base_shipping": 5.50, "free_shipping_threshold": 75.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Pixelatoy", "country_code": "ES", "base_shipping": 6.00, "free_shipping_threshold": 100.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Frikiverso", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 80.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "ActionToys", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 100.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "DVDStoreSpain", "country_code": "ES", "base_shipping": 4.50, "free_shipping_threshold": 50.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Electropolis", "country_code": "ES", "base_shipping": 6.50, "free_shipping_threshold": 150.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Wallapop", "country_code": "ES", "base_shipping": 5.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        
        # Tiendas Europeas (Importación a ES)
        {"shop_name": "DeToyboys", "country_code": "ES", "base_shipping": 15.00, "free_shipping_threshold": 200.0, "vat_multiplier": 1.05, "custom_fees": 0.0, "strategy_key": None},
        {"shop_name": "Time4ActionToysDE", "country_code": "ES", "base_shipping": 18.00, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": None},
        
        # USA (Gran Importación)
        {"shop_name": "BigBadToyStore", "country_code": "ES", "base_shipping": 7.50, "free_shipping_threshold": 0.0, "vat_multiplier": 1.0, "custom_fees": 0.0, "strategy_key": "bbts_flat_rate"}, # Envío $8 (Sin aduanas según experiencia usuario)
    ]

    with SessionCloud() as db:
        for rule_data in rules:
            # Buscar si existe para actualizar o crear
            rule = db.query(LogisticRuleModel).filter(
                LogisticRuleModel.shop_name == rule_data["shop_name"],
                LogisticRuleModel.country_code == rule_data["country_code"]
            ).first()
            
            if rule:
                # Actualizar campos
                for key, value in rule_data.items():
                    setattr(rule, key, value)
                logger.info(f"Actualizada regla logística para {rule_data['shop_name']}")
            else:
                rule = LogisticRuleModel(**rule_data)
                db.add(rule)
                logger.info(f"Añadida regla logística para {rule_data['shop_name']} ({rule_data['country_code']})")
        
        db.commit()
    logger.info("Seed de Oráculo Logístico actualizado (Refinamiento Fase 15.1).")

if __name__ == "__main__":
    seed_logistics()
