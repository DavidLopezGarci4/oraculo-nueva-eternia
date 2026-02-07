
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, CollectionItemModel, PriceHistoryModel, OfferModel, UserModel
from src.core.logger import logger

class VaultService:
    """
    Servicio para la generación y restauración de la 'Eternia Vault' (Bóveda SQLite).
    Implementa el Shield Protocol para seguridad de datos.
    """
    
    def __init__(self, base_vault_path: str = "backups/vaults"):
        self.base_vault_path = base_vault_path
        if not os.path.exists(self.base_vault_path):
            os.makedirs(self.base_vault_path, exist_ok=True)

    def generate_user_vault(self, user_id: int, db_session: Session) -> str:
        """
        Genera un archivo SQLite con los datos exclusivos del usuario.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vault_filename = f"vault_user_{user_id}_{timestamp}.db"
        vault_path = os.path.join(self.base_vault_path, vault_filename)
        
        logger.info(f"🛡️ Generando Bóveda para usuario {user_id} en {vault_path}...")
        
        try:
            # Crear conexión SQLite para la bóveda
            conn = sqlite3.connect(vault_path)
            cursor = conn.cursor()
            
            # 1. Crear Estructura de Tablas (Esquema Espejo)
            cursor.execute('''CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)''')
            cursor.execute('''CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, ean TEXT, category TEXT, master_value REAL)''')
            cursor.execute('''CREATE TABLE collection (id INTEGER PRIMARY KEY, product_id INTEGER, acquired BOOLEAN, condition TEXT, purchase_price REAL, acquired_at TEXT)''')
            
            # 2. Insertar Metadatos (Aislamiento)
            cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("owner_id", str(user_id)))
            cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("version", "1.0"))
            cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("generated_at", datetime.now().isoformat()))
            
            # 3. Exportar Productos en Colección
            col_items = db_session.query(CollectionItemModel).filter(CollectionItemModel.owner_id == user_id).all()
            for item in col_items:
                p = item.product
                cursor.execute(
                    "INSERT INTO products (id, name, ean, category, master_value) VALUES (?, ?, ?, ?, ?)",
                    (p.id, p.name, p.ean, p.category, p.avg_market_price)
                )
                cursor.execute(
                    "INSERT INTO collection (id, product_id, acquired, condition, purchase_price, acquired_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (item.id, item.product_id, item.acquired, item.condition, item.purchase_price, item.acquired_at.isoformat() if item.acquired_at else None)
                )
            
            conn.commit()
            conn.close()
            logger.success(f"✅ Bóveda generada con éxito: {vault_filename}")
            return vault_path
            
        except Exception as e:
            logger.error(f"❌ Error al generar bóveda: {e}")
            try:
                if 'conn' in locals() and conn: conn.close()
                if os.path.exists(vault_path): os.remove(vault_path)
            except Exception as ex:
                logger.warning(f"⚠️ No se pudo limpiar el archivo temporal: {ex}")
            raise

    def stage_vault_import(self, user_id: int, uploaded_file_path: str):
        """
        Implementación inicial del Shield Protocol: Valida y pone en cuarentena.
        (En esta fase simulamos la cuarentena para posterior aprobación Admin)
        """
        logger.info(f"🛡️ Shield Protocol: Iniciando validación de {uploaded_file_path}...")
        
        try:
            # 1. Validación de Bytes Mágicos
            with open(uploaded_file_path, "rb") as f:
                header = f.read(16)
                if header != b"SQLite format 3\x00":
                    raise ValueError("Archivo no es un SQLite válido.")
            
            # 2. Validación de Aislamiento
            conn = sqlite3.connect(uploaded_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = 'owner_id'")
            file_owner_id = cursor.fetchone()
            
            if not file_owner_id or int(file_owner_id[0]) != user_id:
                conn.close()
                raise PermissionError(f"Aislamiento Violado: La bóveda pertenece al usuario {file_owner_id} y no al {user_id}.")
            
            # 3. Validación de Esquema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            required = ["metadata", "products", "collection"]
            for r in required:
                if r not in tables:
                    conn.close()
                    raise ValueError(f"Esquema Corrupto: Falta tabla obligatoria '{r}'.")
            
            conn.close()
            logger.info(f"✅ Shield Protocol superado. Archivo listo para revisión de Admin.")
            return True
            
        except Exception as e:
            logger.critical(f"🔥 Shield Protocol Bloqueó Infección: {e}")
            raise
