
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel

def get_urls():
    with SessionCloud() as db:
        items = db.query(PendingMatchModel).filter(PendingMatchModel.shop_name == 'Wallapop').limit(5).all()
        for item in items:
            print(item.url)

if __name__ == "__main__":
    get_urls()
