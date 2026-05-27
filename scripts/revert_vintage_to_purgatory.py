#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RevertVintage")

# Añadir el root del proyecto al path para poder importar src
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import (
    ProductModel, OfferModel, PendingMatchModel, ProductAliasModel, 
    VintageProductModel, PriceAlertModel, CollectionItemModel, PriceHistoryModel
)

def revert_vintage_to_purgatory():
    logger.info("📡 Conectando a la Base de Datos en la Nube (Supabase)...")
    
    with SessionCloud() as db:
        # 1. Obtener todos los productos marcados como Vintage
        vintage_products = db.query(ProductModel).filter(ProductModel.is_vintage == True).all()
        
        if not vintage_products:
            logger.info("ℹ️ No se encontraron productos vintage en el catálogo actual.")
            return
            
        logger.info(f"🔮 Se encontraron {len(vintage_products)} productos vintage en Eternia. Iniciando secuencia de reversión...")
        
        reverted_offers_count = 0
        
        for product in vintage_products:
            product_name = product.name
            logger.info(f"📦 Procesando producto: '{product_name}' (ID: {product.id})")
            
            # A. Buscar ofertas vinculadas a este producto
            offers = db.query(OfferModel).filter(OfferModel.product_id == product.id).all()
            
            for offer in offers:
                # Crear el registro en el Purgatorio (PendingMatchModel)
                purgatory_item = PendingMatchModel(
                    scraped_name=offer.product.name if offer.product else product_name,
                    ean=product.ean,
                    price=offer.price,
                    currency=offer.currency,
                    url=offer.url,
                    shop_name=offer.shop_name,
                    image_url=offer.image_url,
                    source_type=offer.source_type,
                    is_vintage=True, # Forzar flag vintage en el Purgatorio
                    condition=offer.condition or "Loose",
                    grading=offer.grading or 7.5
                )
                db.add(purgatory_item)
                reverted_offers_count += 1
                
                # Borrar alias específico del anuncio
                db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()
            
            # B. Eliminar historial de precios de las ofertas asociadas
            offer_ids = [offer.id for offer in offers]
            if offer_ids:
                db.query(PriceHistoryModel).filter(PriceHistoryModel.offer_id.in_(offer_ids)).delete(synchronize_session=False)
            
            # C. Eliminar ofertas asociadas
            db.query(OfferModel).filter(OfferModel.product_id == product.id).delete()
            
            # C. Eliminar del modelo vintage si existía
            db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).delete()
            
            # D. Eliminar alias restantes del product_id
            db.query(ProductAliasModel).filter(ProductAliasModel.product_id == product.id).delete()
            
            # E. Eliminar alertas de precio
            db.query(PriceAlertModel).filter(PriceAlertModel.product_id == product.id).delete()
            
            # F. Eliminar posesiones o deseos en la colección
            db.query(CollectionItemModel).filter(CollectionItemModel.product_id == product.id).delete()
            
            # G. Eliminar el producto genérico
            db.delete(product)
            
        try:
            db.commit()
            logger.info("=================================================================")
            logger.info(f"✅ REVERSIÓN COMPLETADA CON ÉXITO EN LA NUBE")
            logger.info(f"   - {len(vintage_products)} productos vintage eliminados de Eternia.")
            logger.info(f"   - {reverted_offers_count} ofertas devueltas al Purgatorio con la bandera Vintage.")
            logger.info("=================================================================")
        except Exception as e:
            logger.error(f"❌ Error al confirmar la transacción: {e}")
            db.rollback()

if __name__ == "__main__":
    revert_vintage_to_purgatory()
