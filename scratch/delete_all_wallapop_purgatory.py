import sys
import logging
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel

# UTF-8 for console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Iniciando eliminación masiva de ítems antiguos de Wallapop en Purgatorio...")
    
    db = SessionCloud()
    try:
        # 1. Consultar registros de Wallapop en el Purgatorio
        query = db.query(PendingMatchModel).filter(PendingMatchModel.shop_name == "Wallapop")
        count = query.count()
        
        logger.info(f"Se encontraron {count} ítems de Wallapop en el Purgatorio listos para ser saneados.")
        
        if count > 0:
            # 2. Ejecutar borrado directo
            query.delete(synchronize_session=False)
            db.commit()
            logger.info(f"¡ÉXITO! Se han eliminado de forma masiva {count} ítems del Purgatorio de Wallapop en Supabase sin meterlos en blacklist.")
        else:
            logger.info("No se encontraron ítems de Wallapop en el Purgatorio.")
            
    except Exception as e:
        logger.error(f"Error crítico en la eliminación masiva: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
