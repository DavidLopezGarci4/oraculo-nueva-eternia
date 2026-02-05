
import sys
from src.infrastructure.collectors.personal_collection import clean_numeric
from scripts.phase0_migration import normalize_us_price, clean_price

def test_currency_detection():
    test_cases = [
        ("$14.99", (14.99, "USD")),
        ("14.99€", (14.99, "EUR")),
        ("20.00 EUR", (20.00, "EUR")),
        ("$1,200.50.", (1200.5, "USD")),
        ("No Price", (0.0, "EUR")),
    ]
    
    for text, expected in test_cases:
        result = clean_numeric(text)
        assert result == expected, f"Failed for {text}: expected {expected}, got {result}"
    print("DONE: Currency detection tests passed!")

def test_migration_logic():
    # Mocking row behavior
    row_usd = {'Avg': '$100.00', 'Currency': 'USD', 'P25': '$80.00'}
    row_eur = {'Avg': '100.00', 'Currency': 'EUR', 'P25': '80.00'}
    
    # Simulating logic from phase0_migration
    avg_usd_raw = clean_price(row_usd.get('Avg'))
    avg_usd_normalized = normalize_us_price(avg_usd_raw)
    
    avg_eur_raw = clean_price(row_eur.get('Avg'))
    avg_eur_normalized = avg_eur_raw # Should stay same in migration logic
    
    assert avg_usd_normalized == 92.0, f"USD normalization failed: {avg_usd_normalized}"
    assert avg_eur_normalized == 100.0, f"EUR normalization failed: {avg_eur_normalized}"
    print("DONE: Migration logic tests passed!")

if __name__ == "__main__":
    try:
        test_currency_detection()
        test_migration_logic()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
