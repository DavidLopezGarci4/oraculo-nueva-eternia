from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ScraperStatusModel

def rename_scraper():
    with SessionCloud() as db:
        status = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == 'kidinn').first()
        if status:
            status.spider_name = 'Tradeinn'
            db.commit()
            print("Successfully renamed 'kidinn' to 'Tradeinn' in ScraperStatus table.")
        else:
            # Check if Tradeinn already exists
            exists = db.query(ScraperStatusModel).filter(ScraperStatusModel.spider_name == 'Tradeinn').first()
            if exists:
                print("'Tradeinn' already exists in ScraperStatus table.")
            else:
                # Create it
                new_status = ScraperStatusModel(spider_name='Tradeinn', status='idle')
                db.add(new_status)
                db.commit()
                print("Created new 'Tradeinn' entry in ScraperStatus table.")

if __name__ == "__main__":
    rename_scraper()
