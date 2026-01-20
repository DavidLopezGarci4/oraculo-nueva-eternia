import asyncio
from src.application.services.deal_scorer import DealScorer
from src.domain.models import ProductModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_deal_scorer():
    print("--- VERIFICANDO DEAL SCORER (PHASE 18) ---")
    
    # 1. Setup Mock Product (MSRP 100, P25 90)
    product = ProductModel(
        name="He-Man Testing",
        retail_price=100.0,
        p25_price=90.0
    )
    
    # Escenario A: Oferta normal (80 EUR)
    # Ahorro MSRP: (100-80)/100 = 20% -> (0.2/0.3)*40 = 26 pts
    # Ventaja P25: (90-80)/90 = 11% -> 40 pts
    # No Wishlist: 0 pts
    # Total esperado: ~66 pts
    score_a = DealScorer.calculate_score(product, 80.0, False)
    print(f"Escenario A (80€): Score = {score_a}")
    
    # Escenario B: Super Ganga en Wishlist (50 EUR)
    # Ahorro MSRP: (100-50)/100 = 50% -> max 40 pts
    # Ventaja P25: (90-50)/90 = 44% -> max 40 pts
    # Wishlist: 20 pts
    # Total esperado: 100 pts
    score_b = DealScorer.calculate_score(product, 50.0, True)
    print(f"Escenario B (50€, Wish): Score = {score_b}")
    
    # Verificar Alerta de Compra Obligatoria
    is_mandatory = DealScorer.is_mandatory_buy(product, 50.0, score_b)
    print(f"Escenario B es Compra Obligatoria? {'YES' if is_mandatory else 'NO'}")

    # Escenario C: Precio Caro (120 EUR)
    score_c = DealScorer.calculate_score(product, 120.0, False)
    print(f"Escenario C (120€): Score = {score_c}")

    if score_b == 100 and is_mandatory and score_c < 20:
        print("\nSUCCESS: DealScorer logic is mathematically sound.")
    else:
        print("\nFAILURE: Score calculation mismatch.")

if __name__ == "__main__":
    asyncio.run(verify_deal_scorer())
