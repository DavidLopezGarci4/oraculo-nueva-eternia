try:
    from vec3.dev.adapters import initialize_runtime
    initialize_runtime()
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from vec3.dev.adapters import initialize_runtime
    initialize_runtime()

from src.application.services.logistics_service import LogisticsService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_logistics():
    # 1. Tradeinn 1 item (2.99)
    p1 = LogisticsService.get_landing_price(20.0, "Tradeinn", "ES", item_count=1)
    # Expected: (20 + 2.99) * 1.0 = 22.99
    logger.info(f"Tradeinn (1 item, 20€): {p1}€ (Expected: 22.99)")
    
    # 2. Tradeinn 10 items (3.49 / 10 = 0.349 per item)
    p10 = LogisticsService.get_landing_price(20.0, "Tradeinn", "ES", item_count=10)
    # Expected: (20*10 + 3.49) / 10 = (200 + 3.49) / 10 = 203.49 / 10 = 20.35
    logger.info(f"Tradeinn (10 items, 20€): {p10}€ (Expected: 20.35)")

    # 3. Electropolis < 100 (3.49)
    pe_low = LogisticsService.get_landing_price(50.0, "Electropolis", "ES", item_count=1)
    # Expected: (50 + 3.49) = 53.49
    logger.info(f"Electropolis (1 item, 50€): {pe_low}€ (Expected: 53.49)")

    # 4. Electropolis > 100 (Free)
    pe_high = LogisticsService.get_landing_price(150.0, "Electropolis", "ES", item_count=1)
    # Expected: 150.0
    logger.info(f"Electropolis (1 item, 150€): {pe_high}€ (Expected: 150.0)")

    # 5. DVDStoreSpain > 60 (Free)
    pd_high = LogisticsService.get_landing_price(70.0, "DVDStoreSpain", "ES", item_count=1)
    # Expected: 70.0
    logger.info(f"DVDStoreSpain (1 item, 70€): {pd_high}€ (Expected: 70.0)")

    # 6. Fantasia Personajes (4.89)
    pf = LogisticsService.get_landing_price(30.0, "Fantasia Personajes", "ES", item_count=1)
    # Expected: 34.89
    logger.info(f"Fantasia Personajes (1 item, 30€): {pf}€ (Expected: 34.89)")

if __name__ == "__main__":
    test_logistics()
