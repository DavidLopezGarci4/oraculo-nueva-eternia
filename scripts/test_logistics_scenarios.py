from src.application.services.logistics_service import LogisticsService
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import LogisticRuleModel

def test_scenarios():
    scenarios = [
        {"shop": "BigBadToyStore", "price": 15.45, "loc": "ES", "expected_desc": "USA Import (8$ ship + 21% VAT on total + 15€ fees)"},
        {"shop": "ActionToys", "price": 21.99, "loc": "ES", "expected_desc": "Local (5€ ship, 0% extra VAT)"},
        {"shop": "Fantasia Personajes", "price": 100.00, "loc": "ES", "expected_desc": "Local (Free shipping threshold 60€)"},
        {"shop": "DeToyboys", "price": 50.00, "loc": "ES", "expected_desc": "EU Import (15€ ship + 5% extra VAT/Adj)"},
    ]

    print(f"{'Shop':<20} | {'Price':<8} | {'Landed':<8} | {'Notes'}")
    print("-" * 60)
    
    for s in scenarios:
        landed = LogisticsService.get_landing_price(s["price"], s["shop"], s["loc"])
        print(f"{s['shop']:<20} | {s['price']:<8.2f} | {landed:<8.2f} | {s['expected_desc']}")

if __name__ == "__main__":
    test_scenarios()
