
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

# Add src to path
sys.path.append(os.getcwd())

from src.core.config import settings
from src.domain.models import Base, ProductModel, ProductAliasModel, UserModel
from src.infrastructure.database import SessionLocal
from src.infrastructure.database_cloud import SessionCloud, init_cloud_db

def cloud_seed():
    logger.info("--- 🚀 INICIANDO VOLCADO MASIVO A LA NUBE (INITIAL SEED) ---")
    
    # 1. Asegurar que las tablas existen en la nube
    logger.info("Paso 1: Inicializando tablas en Supabase (Limpieza Preventiva)...")
    try:
        from src.infrastructure.database_cloud import engine_cloud
        # Borramos todo para asegurar que el nuevo esquema (sub_category, etc) se aplique
        Base.metadata.drop_all(bind=engine_cloud)
        init_cloud_db()
        logger.success("Tablas re-creadas con el nuevo esquema en Cloud.")
    except Exception as e:
        logger.error(f"Error inicializando tablas cloud: {e}")
        return

    # 2. Conectar a local y cloud
    db_local = SessionLocal()
    db_cloud = SessionCloud()

    try:
        # 3. Asegurar que el usuario admin existe en Cloud
        logger.info("Paso 2: Sincronizando usuario Admin...")
        admin_local = db_local.query(UserModel).filter_by(username="admin").first()
        if admin_local:
            admin_cloud = db_cloud.query(UserModel).filter_by(username="admin").first()
            if not admin_cloud:
                new_admin = UserModel(
                    username=admin_local.username,
                    email=admin_local.email,
                    hashed_password=admin_local.hashed_password,
                    role=admin_local.role
                )
                db_cloud.add(new_admin)
                db_cloud.commit()
                logger.info("Admin creado en Cloud.")

        # 4. Migrar Productos
        logger.info("Paso 3: Subiendo catálogo de productos (Mass Insert)...")
        products = db_local.query(ProductModel).all()
        
        # Para evitar colisiones de IDs, borraremos el catálogo cloud si el usuario lo pide, 
        # pero aquí haremos un 'merge' o limpieza previa para un 'Fresh Start'.
        cloud_count = db_cloud.query(ProductModel).count()
        if cloud_count > 0:
            logger.warning(f"La tabla de productos en Cloud ya tiene {cloud_count} items. Limpiando para volcado fresco...")
            # En producción esto sería un riesgo, pero para el 'Initial Seed' del tablero es necesario.
            # Borramos aliases primero por la FK
            db_cloud.query(ProductAliasModel).delete()
            db_cloud.query(ProductModel).delete()
            db_cloud.commit()

        imported = 0
        for p in products:
            new_p = ProductModel(
                name=p.name,
                ean=p.ean,
                image_url=p.image_url,
                category=p.category,
                sub_category=p.sub_category,
                figure_id=p.figure_id,
                variant_name=p.variant_name,
                image_hash=p.image_hash
            )
            db_cloud.add(new_p)
            imported += 1
            if imported % 50 == 0:
                db_cloud.flush()
                logger.info(f"Procesados {imported} productos...")

        db_cloud.commit()
        logger.success(f"¡Catálogo cloud inicializado con {imported} productos!")

        # 5. Migrar Aliases
        logger.info("Paso 4: Sincronizando Aliases de Scraping...")
        aliases = db_local.query(ProductAliasModel).all()
        # Mapeo de IDs (Local -> Cloud) basado en Figure ID o Name+SubCat
        # Para simplicidad en el seed si el orden es el mismo, pero mejor buscar por figure_id
        for a in aliases:
            # Buscar el producto correspondiente en cloud
            p_local = db_local.query(ProductModel).get(a.product_id)
            if p_local:
                p_cloud = db_cloud.query(ProductModel).filter_by(figure_id=p_local.figure_id).first()
                if p_cloud:
                    new_alias = ProductAliasModel(
                        product_id=p_cloud.id,
                        source_url=a.source_url,
                        confirmed=a.confirmed
                    )
                    db_cloud.add(new_alias)
        
        db_cloud.commit()
        logger.success("Aliases sincronizados.")

    except Exception as e:
        logger.error(f"Error durante el volcado: {e}")
        db_cloud.rollback()
    finally:
        db_local.close()
        db_cloud.close()

    logger.info("--- ✅ VOLCADO MASIVO FINALIZADO ---")

if __name__ == "__main__":
    cloud_seed()
