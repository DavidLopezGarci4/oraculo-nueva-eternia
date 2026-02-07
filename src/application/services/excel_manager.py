
import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import CollectionItemModel, ProductModel
from src.core.logger import logger

class ExcelManager:
    """
    Gestor del Excel Bridge para sincronización de inventario David.
    Mantiene el Excel local actualizado con los datos del Oráculo.
    """
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path

    def sync_acquisitions_from_db(self, user_id: int):
        """
        Lee la DB y actualiza el Excel local.
        Busca la columna 'Adquirido' y la marca como SÍ/NO según la colección.
        """
        if not os.path.exists(self.excel_path):
            logger.warning(f"⚠️ Excel no encontrado en {self.excel_path}. Operación cancelada.")
            return False

        try:
            logger.info(f"📊 Sincronizando Excel Bridge: {os.path.basename(self.excel_path)}...")
            
            # Cargar Excel
            df = pd.read_excel(self.excel_path)
            
            # Obtener colección actual de la DB
            with SessionCloud() as db:
                collection = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == user_id).all()
                collection_map = {item.product.name.lower(): item.acquired for item in collection}
            
            # Asegurar que existe la columna 'Adquirido' (o crearla si no existe, pero David dice que ya está)
            col_name = None
            for col in df.columns:
                if 'adquirido' in col.lower():
                    col_name = col
                    break
            
            if not col_name:
                logger.warning("⚠️ No se encontró la columna 'Adquirido' en el Excel. Creándola...")
                df['Adquirido'] = 'NO'
                col_name = 'Adquirido'

            # Actualizar valores
            # Suponemos que la primera columna o una columna 'Nombre' tiene el nombre del producto
            name_col = df.columns[0] # Fallback a la primera columna
            for idx, row in df.iterrows():
                product_name = str(row[name_col]).lower()
                if product_name in collection_map:
                    df.at[idx, col_name] = 'SÍ' if collection_map[product_name] else 'NO'

            # Guardar cambios
            df.to_excel(self.excel_path, index=False)
            logger.success(f"✅ Excel Bridge sincronizado: {len(collection_map)} items validados.")
            return True

        except Exception as e:
            logger.error(f"❌ Error en Excel Bridge: {e}")
            return False

    def export_full_backup(self, user_id: int, output_path: str):
        """
        Genera un nuevo Excel completo con todos los datos del usuario como respaldo puro.
        """
        try:
            with SessionCloud() as db:
                items = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == user_id).all()
                data = []
                for it in items:
                    data.append({
                        "ID": it.product.id,
                        "Producto": it.product.name,
                        "EAN": it.product.ean,
                        "Categoría": it.product.category,
                        "Adquirido": "SÍ" if it.acquired else "NO",
                        "Estado": it.condition,
                        "Precio Compra": it.purchase_price,
                        "Fecha": it.acquired_at
                    })
                
                df = pd.DataFrame(data)
                df.to_excel(output_path, index=False)
                logger.success(f"🛡️ Resguardo Humano generado: {output_path}")
                return True
        except Exception as e:
            logger.error(f"❌ Error al generar resguardo Excel: {e}")
            return False
