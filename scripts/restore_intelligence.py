import sqlite3
import os
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from src.domain.models import ProductModel, OfferModel, CollectionItemModel
from src.infrastructure.database_cloud import SessionCloud as SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recovery_service")

def recover_and_normalize():
    print("--- ORACULO: OPERACION RESTAURACION ---")
    
    # 1. Reparar Esquema si es necesario
    db_path = "oraculo.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Renombrar origin_category a source_type si aun existe
    for table in ["offers", "pending_matches"]:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        if "origin_category" in cols and "source_type" not in cols:
            print(f"Fixing schema for {table}...")
            cursor.execute(f"ALTER TABLE {table} RENAME COLUMN origin_category TO source_type")

    conn.commit()
    conn.close()

    # 2. Normalizar datos y recalcular scores
    db = SessionLocal()
    try:
        offers = db.query(OfferModel).all()
        print(f"Procesando {len(offers)} ofertas para normalizacion...")
        
        updated_count = 0
        for offer in offers:
            # Normalizar Categoria (Case Sensitivity Fix)
            if offer.source_type and offer.source_type.lower() == 'retail':
                offer.source_type = 'Retail'
            elif offer.source_type and offer.source_type.lower() in ['peer-to-peer', 'p2p']:
                offer.source_type = 'Peer-to-Peer'
            
            # Recalcular Opportunity Score con Landed Price
            # (Usamos Localizacion ES por defecto para la restauracion)
            landed_price = LogisticsService.get_landing_price(offer.price, offer.shop_name, "ES")
            
            # Verificar si esta en wishlist
            is_wish = db.query(CollectionItemModel).filter(
                CollectionItemModel.product_id == offer.product_id,
                CollectionItemModel.owner_id == 2, # David
                CollectionItemModel.acquired == False
            ).first() is not None
            
            if offer.product:
                offer.opportunity_score = DealScorer.calculate_score(offer.product, landed_price, is_wish)
                updated_count += 1
        
        db.commit()
        print(f" Exito: {updated_count} ofertas normalizadas y puntuadas.")
        
    except Exception as e:
        db.rollback()
        print(f" Error durante la recuperacion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    recover_and_normalize()
