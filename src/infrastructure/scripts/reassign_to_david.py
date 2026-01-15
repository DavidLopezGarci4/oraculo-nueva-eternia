from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import CollectionItemModel, UserModel
from loguru import logger

def reassign_collection():
    db = SessionCloud()
    try:
        # 1. Verificar IDs
        admin = db.query(UserModel).filter(UserModel.username == "admin").first()
        david = db.query(UserModel).filter(UserModel.username == "David").first()
        
        if not admin or not david:
            logger.error(f"Usuarios no encontrados: Admin={admin}, David={david}")
            return

        logger.info(f"Iniciando reasignación: Admin (ID {admin.id}) -> David (ID {david.id})")

        # 2. Contar items actuales
        admin_items = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == admin.id).all()
        logger.info(f"Items encontrados en Admin: {len(admin_items)}")

        if not admin_items:
            logger.warning("No hay items para reasignar.")
            return

        # 3. Ejecutar Update Masivo
        updated_count = db.query(CollectionItemModel).filter(
            CollectionItemModel.owner_id == admin.id
        ).update({CollectionItemModel.owner_id: david.id})

        db.commit()
        logger.success(f"¡Éxito! {updated_count} items reasignados correctamente a David.")

        # 4. Verificación final
        final_david_count = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == david.id).count()
        logger.info(f"Conteo final en cuenta de David: {final_david_count}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error durante la migración: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reassign_collection()
