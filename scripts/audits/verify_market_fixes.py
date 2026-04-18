
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.infrastructure.database_cloud import SessionCloud
from src.application.services.market_intelligence import MarketIntelligenceService
from src.domain.models import ProductModel, OfferModel, PriceHistoryModel

def verify_market_intelligence():
    db = SessionCloud()
    service = MarketIntelligenceService(db)
    
    # Let's find some products to test
    products = db.query(ProductModel).limit(3).all()
    
    if not products:
        print("[ERR] No products found in database to test.")
        return

    print(f"[INFO] Verificando Inteligencia de Mercado 3OX para {len(products)} productos...\n")

    for p in products:
        print(f"--- Producto: {p.name} (ID: {p.id}) ---")
        summary = service.get_market_summary(p.id)
        
        # Check Evolution
        evo = summary.get('evolution', {})
        retail_evo = evo.get('Retail', [])
        p2p_evo = evo.get('Peer-to-Peer', [])
        
        print(f"EVO Retail: {len(retail_evo)} puntos")
        print(f"EVO P2P: {len(p2p_evo)} puntos")
        
        # Check Bid Strategy
        bid = summary.get('bid_strategy', {})
        print(f"Ideal Bid: {bid.get('ideal_bid')} EURO")
        print(f"Confidencia: {bid.get('confidence')}")
        print(f"Razon: {bid.get('reason')}")
        print(f"Muestras: {bid.get('total_samples', 0)}")
        print("\n")

    db.close()

if __name__ == "__main__":
    verify_market_intelligence()
