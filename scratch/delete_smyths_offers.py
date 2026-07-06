import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, PriceHistoryModel, PendingMatchModel

def delete_smyths_offers():
    print("Conectando a Supabase (Produccion) para purgar ofertas de SmythsToys...")
    
    with SessionCloud() as db:
        try:
            # 1. Purgar del Purgatorio (pending_matches)
            pending_deleted = db.query(PendingMatchModel).filter(PendingMatchModel.shop_name == "SmythsToys").delete(synchronize_session=False)
            print(f"Eliminadas {pending_deleted} ofertas de SmythsToys de la tabla pending_matches (Purgatorio).")
            
            # 2. Encontrar ofertas de SmythsToys en la tabla principal (offers)
            offers = db.query(OfferModel).filter(OfferModel.shop_name == "SmythsToys").all()
            offer_ids = [o.id for o in offers]
            
            if offer_ids:
                print(f"Encontradas {len(offer_ids)} ofertas de SmythsToys en la tabla principal.")
                # Eliminar historial de precios asociado
                history_deleted = db.query(PriceHistoryModel).filter(PriceHistoryModel.offer_id.in_(offer_ids)).delete(synchronize_session=False)
                print(f"Eliminados {history_deleted} registros de historial de precios.")
                # Eliminar ofertas de la tabla principal
                offers_deleted = db.query(OfferModel).filter(OfferModel.id.in_(offer_ids)).delete(synchronize_session=False)
                print(f"Eliminadas {offers_deleted} ofertas de SmythsToys de la tabla principal.")
            else:
                print("No se encontraron ofertas de SmythsToys en la tabla principal (offers).")
            
            # Confirmar cambios
            db.commit()
            print("Purgado de base de datos completado con exito!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error al eliminar ofertas de la base de datos: {e}")

if __name__ == "__main__":
    delete_smyths_offers()
