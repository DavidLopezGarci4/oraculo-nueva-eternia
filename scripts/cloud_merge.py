
import json
import sqlite3
import os
import sys
from loguru import logger
from sqlalchemy.orm import Session
from datetime import datetime

# Add src to path
sys.path.append(os.getcwd())

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, CollectionItemModel, BlackcludedItemModel, UserModel

def cloud_merge():
    logger.info("--- 🧬 INICIANDO FUSIÓN INTELIGENTE DE DATOS ---")
    
    # 1. Rutas
    old_db_path = 'C:/Users/dace8/OneDrive/Documentos/Antigravity/el-oraculo-de-eternia/oraculo.db'
    backup_dir = 'backups/cloud'
    collection_json = os.path.join(backup_dir, 'collection_items.json')
    blacklist_json = os.path.join(backup_dir, 'blackcluded_items.json')
    users_json = os.path.join(backup_dir, 'users.json')

    if not os.path.exists(old_db_path):
        logger.error(f"Base de datos antigua no encontrada en {old_db_path}")
        return

    # 2. Mapeo Nombre -> ID (Nube)
    db_cloud = SessionCloud()
    cloud_products = db_cloud.query(ProductModel).all()
    name_to_cloud_id = {p.name.strip().lower(): p.id for p in cloud_products}
    logger.info(f"Cargados {len(name_to_cloud_id)} nombres de productos en la nube.")

    # 3. Mapeo ID Viejo -> Nombre (SQLite)
    old_id_to_name = {}
    try:
        conn = sqlite3.connect(old_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM products")
        for old_id, name in cursor.fetchall():
            old_id_to_name[old_id] = name.strip().lower()
        conn.close()
        logger.info(f"Cargado mapeo de {len(old_id_to_name)} IDs antiguos.")
    except Exception as e:
        logger.error(f"Error leyendo base de datos antigua: {e}")
        return

    # 4. Restaurar BLACKLIST
    if os.path.exists(blacklist_json):
        logger.info("Paso 1: Restaurando Blacklist...")
        with open(blacklist_json, 'r', encoding='utf-8') as f:
            blacklist_data = json.load(f)
        
        added_bl = 0
        for item in blacklist_data:
            exists = db_cloud.query(BlackcludedItemModel).filter_by(url=item['url']).first()
            if not exists:
                new_bl = BlackcludedItemModel(
                    url=item['url'],
                    scraped_name=item['scraped_name'],
                    reason=item.get('reason', 'user_discarded'),
                    created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else datetime.utcnow()
                )
                db_cloud.add(new_bl)
                added_bl += 1
        db_cloud.commit()
        logger.success(f"Restaurados {added_bl} items en la Blacklist.")

    # 4.5 Restaurar USUARIOS (David)
    david_id = 1 # Fallback
    if os.path.exists(users_json):
        logger.info("Paso 1.5: Restaurando Usuario David...")
        with open(users_json, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        for u in users_data:
            exists = db_cloud.query(UserModel).filter_by(username=u['username']).first()
            if not exists:
                new_user = UserModel(
                    username=u['username'],
                    email=u['email'],
                    hashed_password=u['hashed_password'],
                    role=u.get('role', 'viewer')
                )
                db_cloud.add(new_user)
                db_cloud.flush()
                if u['username'] == 'David':
                    david_id = new_user.id
            else:
                if u['username'] == 'David':
                    david_id = exists.id
        db_cloud.commit()
        logger.success(f"Usuario David identificado con ID {david_id}")

    # 5. Restaurar COLECCIÓN
    if os.path.exists(collection_json):
        logger.info("Paso 2: Restaurando Colección Personal para usuario David...")
        with open(collection_json, 'r', encoding='utf-8') as f:
            collection_data = json.load(f)
        
        matched = 0
        missed = 0
        for item in collection_data:
            # En el backup original (el_oraculo), David era ID 1.
            # Solo migramos items que pertenecían a David (ID 1 en el backup) o todos?
            # El usuario dice que su colección tiene 75 items.
            if item.get('owner_id') != 1: # Si David no era el 1, esto puede fallar. En el JSON David es 1.
                continue

            old_pid = item['product_id']
            p_name = old_id_to_name.get(old_pid)
            
            if p_name and p_name in name_to_cloud_id:
                new_pid = name_to_cloud_id[p_name]
                
                # Evitar duplicados en colección
                exists = db_cloud.query(CollectionItemModel).filter_by(product_id=new_pid, owner_id=david_id).first()
                if not exists:
                    new_item = CollectionItemModel(
                        product_id=new_pid,
                        owner_id=david_id,
                        acquired=item.get('acquired', False),
                        condition=item.get('condition', 'New'),
                        notes=item.get('notes'),
                        acquired_at=datetime.fromisoformat(item['acquired_at']) if item.get('acquired_at') else datetime.utcnow()
                    )
                    db_cloud.add(new_item)
                    matched += 1
            else:
                missed += 1
                # logger.warning(f"No match for item: {p_name if p_name else 'ID ' + str(old_pid)}")
        
        db_cloud.commit()
        logger.success(f"Colección sincronizada: {matched} items vinculados, {missed} items sin correspondencia en el nuevo catálogo.")

    db_cloud.close()
    logger.info("--- ✅ PROCESO DE FUSIÓN COMPLETADO ---")

if __name__ == "__main__":
    cloud_merge()
