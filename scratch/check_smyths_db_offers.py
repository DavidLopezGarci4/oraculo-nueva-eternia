import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())

# Load environment
load_dotenv(override=True)

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel

def check_offers():
    print("Conectando a Supabase para verificar ofertas de SmythsToys en Purgatorio...")
    with SessionCloud() as db:
        offers = db.query(PendingMatchModel).filter(PendingMatchModel.shop_name == "SmythsToys").all()
        print(f"Total ofertas en Purgatorio: {len(offers)}")
        for idx, o in enumerate(offers[:10]):
            print(f"{idx+1:02d}. Nombre: {o.scraped_name}")
            print(f"    URL Imagen: {o.image_url}")
            print(f"    Precio: {o.price}")
            print(f"    URL: {o.url}")

if __name__ == "__main__":
    check_offers()
