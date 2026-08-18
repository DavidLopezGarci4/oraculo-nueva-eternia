import pytest
from src.application.services.logistics_service import LogisticsService
from src.application.services.currency_service import CurrencyService
from src.domain.models import LogisticRuleModel, OfferModel, ProductModel, CollectionItemModel
from src.infrastructure.database_cloud import SessionCloud

def test_bbts_landing_price_calculation(client):
    usd_rate = CurrencyService.get_usd_to_eur_rate()
    # 25 USD figure -> (25 + 8) * usd_rate * 1.21
    expected = round((25.0 + 8.0) * usd_rate * 1.21, 2)
    landed = LogisticsService.get_landing_price(25.0, 'BigBadToyStore', 'ES')
    assert landed == expected

def test_p2p_insurance_and_shipping(client):
    # Wallapop: 20 EUR figure -> 20 * 1.02 + 5.00 = 25.40
    landed_wallapop = LogisticsService.get_landing_price(20.0, 'Wallapop', 'ES')
    assert landed_wallapop == 25.40

    # Vinted: 30 EUR figure -> 30 * 1.02 + 5.00 = 35.60
    landed_vinted = LogisticsService.get_landing_price(30.0, 'Vinted', 'ES')
    assert landed_vinted == 35.60

    # Ebay.es: 50 EUR figure -> 50 * 1.02 + 5.00 = 56.00
    landed_ebay = LogisticsService.get_landing_price(50.0, 'Ebay.es', 'ES')
    assert landed_ebay == 56.00

def test_triguetech_flat_rate(client):
    # 1 item: 20 + 7 = 27
    assert LogisticsService.get_landing_price(20.0, 'Triguetech', 'ES', item_count=1) == 27.00
    # 2 items in bulk calculation: (40 + 7) / 2 = 23.50 per unit
    assert LogisticsService.get_landing_price(20.0, 'Triguetech', 'ES', item_count=2) == 23.50

def test_frikimaz_threshold(client):
    # Under 69€: 50 + 5 = 55
    assert LogisticsService.get_landing_price(50.0, 'Frikimaz', 'ES') == 55.00
    # Over 69€: 70 + 0 = 70
    assert LogisticsService.get_landing_price(70.0, 'Frikimaz', 'ES') == 70.00

def test_smythstoys_shipping(client):
    # 30 + 4 = 34
    assert LogisticsService.get_landing_price(30.0, 'SmythsToys', 'ES') == 34.00

def test_shop_aliases_normalization(client):
    # Toymi maps to ToymiEU (5.50€)
    assert LogisticsService.get_landing_price(20.0, 'Toymi', 'ES') == 25.50
    assert LogisticsService.get_landing_price(20.0, 'ToymiEU', 'ES') == 25.50

    # WallapopManual maps to Wallapop (20 * 1.02 + 5 = 25.40)
    assert LogisticsService.get_landing_price(20.0, 'WallapopManual', 'ES') == 25.40

    # Tradeinn (Kidinn) maps to Tradeinn (20 + 2.99 = 22.99)
    assert LogisticsService.get_landing_price(20.0, 'Tradeinn (Kidinn)', 'ES') == 22.99

def test_calculate_cart_breakdown(client):
    cart_items = [
        {'shop_name': 'Wallapop', 'product_name': 'Item 1', 'price': 20.0, 'quantity': 1},
        {'shop_name': 'Frikimaz', 'product_name': 'Item 2', 'price': 75.0, 'quantity': 1},
        {'shop_name': 'Triguetech', 'product_name': 'Item 3', 'price': 15.0, 'quantity': 2},
    ]
    invoice = LogisticsService.calculate_cart(cart_items, 'ES')
    assert invoice['grand_total_eur'] > 0
    assert len(invoice['breakdown']) == 3

    shops = {b['shop']: b for b in invoice['breakdown']}
    assert shops['Wallapop']['shipping_eur'] == 5.00
    assert shops['Wallapop']['tax_eur'] == 0.40 # 2% of 20
    assert shops['Wallapop']['total_eur'] == 25.40

    assert shops['Frikimaz']['shipping_eur'] == 0.00 # Free > 69€
    assert shops['Frikimaz']['total_eur'] == 75.00

    assert shops['Triguetech']['shipping_eur'] == 7.00 # Flat 7€
    assert shops['Triguetech']['total_eur'] == 37.00 # 30 + 7
