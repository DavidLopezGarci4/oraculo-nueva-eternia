from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductAliasModel

def get_link():
    with SessionCloud() as db:
        alias = db.query(ProductAliasModel).filter(ProductAliasModel.source_url.contains("actionfigure411")).first()
        if alias:
            print(f"Detail Link: {alias.source_url}")

if __name__ == "__main__":
    get_link()
