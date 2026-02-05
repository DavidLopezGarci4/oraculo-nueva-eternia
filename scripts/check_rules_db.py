from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import LogisticRuleModel
import logging

logging.basicConfig(level=logging.INFO)

def check_rules():
    with SessionCloud() as db:
        rules = db.query(LogisticRuleModel).filter(LogisticRuleModel.shop_name == 'BigBadToyStore').all()
        print(f"--- BBTS RULES IN DB ---")
        for r in rules:
            print(f"ID: {r.id}, Shop: {r.shop_name}, Country: {r.country_code}, VAT: {r.vat_multiplier}, Strategy: {r.strategy_key}")

if __name__ == "__main__":
    check_rules()
