from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from loguru import logger
import json
import os
import re
import sys
from datetime import datetime
from sqlalchemy import func, select, and_, desc, text, or_
from src.core.config import settings
from src.infrastructure.database_cloud import SessionCloud, engine_cloud
from src.domain.models import (
    ProductModel, OfferModel, PendingMatchModel, CollectionItemModel,
    UserModel, ScraperStatusModel, BlackcludedItemModel, ScraperExecutionLogModel,
    OfferHistoryModel, LogisticRuleModel, ProductAliasModel,
    AuthorizedDeviceModel,
)
from src.application.services.logistics_service import LogisticsService
from src.application.services.deal_scorer import DealScorer
from src.core.security import SecurityShield
from src.interfaces.api.deps import (
    verify_api_key,
    verify_device,
    ensure_scrapers_registered,
)
from src.interfaces.api.schemas import (
    CartItem,
    CartRequest,
    CreateUserRequest,
    UserRoleUpdateRequest,
    HeroOutput,
    SyncAction,
    ProductOutput,
    ProductEditRequest,
    ProductMergeRequest,
    CollectionToggleRequest,
    CollectionItemUpdateRequest,
    PurgatoryMatchRequest,
    PurgatoryDiscardRequest,
    PurgatoryBulkDiscardRequest,
    AnomalyValidationRequest,
    RelinkOfferRequest,
    WallapopProduct,
    WallapopImportRequest,
)
from src.interfaces.api.routers import auth as auth_router
from src.interfaces.api.routers import health as health_router
from src.interfaces.api.routers import scrapers as scrapers_router

app = FastAPI(title="Oráculo API Broker", version="1.0.0")

# ----------------------

# Call at startup
try:
    from src.infrastructure.database_cloud import init_cloud_db
    init_cloud_db()
    ensure_scrapers_registered()
except Exception as e:
    logger.error(f"Startup initialization failed: {e}")

# Configurar CORS para permitir peticiones universales (Útil para acceso móvil y Docker)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitimos todo para facilitar el acceso desde cualquier IP del hogar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers extraídos por dominio (paso 1 de modularización)
app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(scrapers_router.router)


@app.post("/api/admin/users/create")
async def create_user(request: CreateUserRequest, x_api_key: str = Depends(verify_api_key)):
    """
    Crea un nuevo Guardián en el sistema. Reservado para el Arquitecto.
    """
    with SessionCloud() as db:
        # Verificar duplicados
        exists = db.query(UserModel).filter(or_(UserModel.email == request.email, UserModel.username == request.username)).first()
        if exists:
            raise HTTPException(status_code=400, detail="El usuario o email ya existe.")
            
        new_user = UserModel(
            username=request.username,
            email=request.email,
            hashed_password=SecurityShield.hash_password(request.password),
            role=request.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"👤 Nuevo Guardián creado: {new_user.username} ({new_user.role})")
        return {"status": "success", "message": f"Héroe {new_user.username} registrado."}

@app.get("/api/admin/users", response_model=List[HeroOutput], dependencies=[Depends(verify_api_key)])
async def get_all_heroes(db_session: SessionCloud = Depends(lambda: SessionCloud())):
    """
    Lista todos los héroes con su conteo real de items en colección.
    """
    with db_session as db:
        # Subconsulta para contar items por usuario
        counts = db.query(
            CollectionItemModel.owner_id,
            func.count(CollectionItemModel.id).label("item_count")
        ).group_by(CollectionItemModel.owner_id).subquery()

        # Join UserModel con el conteo
        users = db.query(
            UserModel,
            func.coalesce(counts.c.item_count, 0).label("collection_size")
        ).outerjoin(counts, UserModel.id == counts.c.owner_id).all()

        results = []
        for user, count in users:
            results.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "location": user.location,
                "collection_size": count
            })
        return results

@app.patch("/api/admin/users/{user_id}/role", dependencies=[Depends(verify_api_key)])
async def update_hero_role(user_id: int, request: UserRoleUpdateRequest):
    """
    Actualiza el rango (rol) de un héroe en el Oráculo.
    """
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Héroe no encontrado")
        
        user.role = request.role
        db.commit()
        return {"status": "success", "message": f"Rango de {user.username} actualizado a {request.role}"}

@app.post("/api/admin/users/{user_id}/reset-password", dependencies=[Depends(verify_api_key)])
async def reset_hero_password(user_id: int):
    """
    Registra una solicitud de reseteo de contraseña para un héroe.
    En el futuro, esto enviará un email con un token.
    """
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Héroe no encontrado")
        
        logger.warning(f"🛡️ PROTOCOLO DE RESETEO: Solicitud de cambio de contraseña para {user.username} ({user.email})")
        return {"status": "success", "message": f"Protocolo de reseteo iniciado para {user.email}"}

@app.delete("/api/admin/users/{user_id}", dependencies=[Depends(verify_api_key)])
async def delete_hero(user_id: int):
    """
    ELIMINACIÓN DEFINITIVA: Borra a un usuario y sus pertenencias del Oráculo.
    (Admin Only - ACCIÓN IRREVERSIBLE)
    """
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Héroe no encontrado")
        
        if user.role == "admin":
            raise HTTPException(status_code=403, detail="No se puede eliminar a un Arquitecto del sistema.")

        # 1. Borrar items de su colección asociados
        db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == user.id).delete()
        
        # 2. Borrar registro de usuario
        username = user.username
        db.delete(user)
        db.commit()
        
        logger.warning(f"🗑️ Héroe Eliminado: '{username}' (ID: {user_id}) ha sido borrado por el Arquitecto.")
        return {"status": "success", "message": f"Justicia del Arquitecto: El héroe '{username}' ha sido purgado de los registros."}

@app.get("/api/products", response_model=List[ProductOutput])
async def get_products():
    """Retorna el catálogo maestro completo para búsquedas en el Purgatorio."""
    with SessionCloud() as db:
        # Subconsulta para encontrar el precio mínimo por producto (P2P activa)
        subq = (
            select(
                OfferModel.product_id,
                func.min(OfferModel.price).label("min_price")
            )
            .where(OfferModel.source_type == "Peer-to-Peer")
            .where(OfferModel.is_available == True)
            .group_by(OfferModel.product_id)
            .subquery()
        )
        
        # Consulta principal con LEFT JOIN para traer todos los productos
        # aunque no tengan ofertas P2P
        query = (
            select(ProductModel, OfferModel)
            .outerjoin(subq, ProductModel.id == subq.c.product_id)
            .outerjoin(OfferModel, and_(
                OfferModel.product_id == ProductModel.id,
                OfferModel.price == subq.c.min_price,
                OfferModel.source_type == "Peer-to-Peer",
                OfferModel.is_available == True
            ))
            .distinct(ProductModel.id)
        )
        
        results = db.execute(query).all()
        
        final_products = []
        for product, best_offer in results:
            po = ProductOutput.model_validate(product)
            po.avg_market_price = product.avg_market_price or 0.0
            if best_offer:
                po.best_p2p_price = best_offer.price
                po.best_p2p_source = best_offer.shop_name
            final_products.append(po)
            
        return final_products

@app.get("/api/products/search")
async def search_products(q: str = ""):
    """
    Endpoint ultra-ligero para búsquedas rápidas (Ej: Relink Drawer).
    Retorna solo lo mínimo necesario para identificar el producto.
    """
    if len(q) < 2:
        return []
        
    with SessionCloud() as db:
        query = select(ProductModel).where(
            (ProductModel.name.ilike(f"%{q}%")) | 
            (ProductModel.figure_id.ilike(f"%{q}%"))
        ).limit(20)
        
        result = db.execute(query)
        products = result.scalars().all()
        return [
            {
                "id": p.id, 
                "name": p.name, 
                "figure_id": p.figure_id, 
                "sub_category": p.sub_category,
                "image_url": p.image_url
            } for p in products
        ]

@app.get("/api/auctions/products", response_model=List[ProductOutput])
async def get_auction_products():
    """
    Retorna productos que tienen ofertas de subastas activas (Wallapop/eBay).
    """
    with SessionCloud() as db:
        # Consulta optimizada que trae el producto y su mejor oferta P2P
        from sqlalchemy import func
        
        # Subconsulta para encontrar el precio mínimo por producto
        subq = (
            select(
                OfferModel.product_id,
                func.min(OfferModel.price).label("min_price")
            )
            .where(OfferModel.source_type == "Peer-to-Peer")
            .where(OfferModel.is_available == True)
            .group_by(OfferModel.product_id)
            .subquery()
        )
        
        # Consulta principal que une producto con su mejor oferta para obtener el shop_name
        query = (
            select(ProductModel, OfferModel)
            .join(subq, ProductModel.id == subq.c.product_id)
            .join(OfferModel, and_(
                OfferModel.product_id == ProductModel.id,
                OfferModel.price == subq.c.min_price,
                OfferModel.source_type == "Peer-to-Peer",
                OfferModel.is_available == True
            ))
            .distinct(ProductModel.id) # Asegurar un solo resultado por producto si hay empates de precio
        )
        
        results = db.execute(query).all()
        
        output = []
        for product, best_offer in results:
            # Convertimos a ProductOutput (manualmente para asegurar campos extra)
            p_out = ProductOutput.model_validate(product)
            p_out.best_p2p_price = best_offer.price
            p_out.best_p2p_source = best_offer.shop_name
            
            # --- PHASE 44: LIVE ANALYTICS (FALLBACK) ---
            # Si las estadísticas calculadas en el modelo son 0, intentamos un cálculo rápido live
            if p_out.avg_retail_price == 0 or p_out.avg_p2p_price == 0:
                offers = db.query(OfferModel).filter(OfferModel.product_id == product.id, OfferModel.is_available == True).all()
                retail_prices = [o.price for o in offers if o.source_type == "Retail"]
                p2p_prices = [o.price for o in offers if o.source_type == "Peer-to-Peer"]
                
                if retail_prices:
                    p_out.avg_retail_price = round(sum(retail_prices) / len(retail_prices), 2)
                if p2p_prices:
                    p_out.avg_p2p_price = round(sum(p2p_prices) / len(p2p_prices), 2)
            
            output.append(p_out)
            
        return output

@app.get("/api/intelligence/market/{product_id}", dependencies=[Depends(verify_api_key)])
async def get_market_intelligence(product_id: int):
    """
    Retorna el estudio de mercado para un producto (Estadísticas 3OX).
    """
    from src.application.services.market_intelligence import MarketIntelligenceService
    with SessionCloud() as db:
        service = MarketIntelligenceService(db)
        summary = service.get_market_summary(product_id)
        if not summary or summary == {}:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return summary

@app.get("/api/wallapop/preview", dependencies=[Depends(verify_api_key)])
async def get_wallapop_preview(url: str):
    """
    Puente de Visión (Phase 40): Obtiene detalles de un item de Wallapop 
    suplantando el navegador para evitar el error 403.
    """
    from src.application.services.wallapop_bridge import WallapopBridge
    details = await WallapopBridge.get_item_details(url)
    if not details:
        raise HTTPException(status_code=404, detail="No se pudo invocar el espíritu de Wallapop")
    return details

@app.get("/api/collection", response_model=List[ProductOutput])
async def get_collection(user_id: int):
    """
    Retorna la colección personal del usuario desde Supabase.
    """
    from src.domain.models import CollectionItemModel, OfferModel
    from src.application.services.valuation_service import ValuationService
    
    with SessionCloud() as db:
        # 0. Initialize Valuation service
        valuation_service = ValuationService(db)

        # 1. Fetch Location
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user: user_location = user.location

        # 2. Fetch Products + Collection Data
        query = (
            select(ProductModel, CollectionItemModel)
            .join(CollectionItemModel, ProductModel.id == CollectionItemModel.product_id)
            .where(CollectionItemModel.owner_id == user_id)
        )
        results = db.execute(query).all()
        
        if not results:
            return []

        output_list = []
        for product, collection_item in results:
            market_val = valuation_service.get_consolidated_value(product, user_location)
            
            # Smart Grail Logic (Simplified based on best available value)
            is_grail = False
            grail_score = 0.0
            if market_val > 0 and product.retail_price and product.retail_price > 0:
                roi = ((market_val - product.retail_price) / product.retail_price) * 100 
                if roi > 100: # Threshold for Grail
                    is_grail = True
                    grail_score = min(roi / 10, 100)

            output_list.append(ProductOutput(
                id=product.id,
                name=product.name,
                ean=product.ean,
                image_url=product.image_url,
                category=product.category,
                sub_category=product.sub_category,
                figure_id=product.figure_id,
                variant_name=product.variant_name,
                purchase_price=collection_item.purchase_price or 0.0,
                market_value=round(market_val, 2),
                avg_market_price=product.avg_market_price or 0.0,
                p25_price=product.p25_price or 0.0,
                landing_price=round(market_val, 2), # Using consolidated market_val as landing estimate
                is_grail=is_grail,
                grail_score=round(grail_score, 1),
                is_wish=not collection_item.acquired,
                acquired_at=collection_item.acquired_at.isoformat() if collection_item.acquired_at else None,
                condition=collection_item.condition or "New",
                grading=collection_item.grading or 10.0,
                notes=collection_item.notes
            ))
        
        return output_list

@app.put("/api/products/{product_id}", dependencies=[Depends(verify_api_key)])
async def edit_product(product_id: int, request: ProductEditRequest):
    """
    Actualiza metadatos de un producto (Editor de la Verdad).
    """
    with SessionCloud() as db:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if request.name is not None: product.name = request.name
        if request.ean is not None: product.ean = request.ean
        if request.image_url is not None: product.image_url = request.image_url
        if request.category is not None: product.category = request.category
        if request.sub_category is not None: product.sub_category = request.sub_category
        if request.retail_price is not None: product.retail_price = request.retail_price
        
        db.commit()
        return {"status": "success", "message": f"Reliquia '{product.name}' actualizada con éxito"}

@app.get("/api/admin/duplicates", dependencies=[Depends(verify_api_key)])
async def get_duplicates():
    """
    Detecta posibles duplicados basados en EAN (Exacto).
    """
    with SessionCloud() as db:
        products = db.query(ProductModel).all()
        duplicates = []
        
        # Exact EAN Match
        ean_map = {}
        for p in products:
            if p.ean:
                product_info = {
                    "id": p.id,
                    "name": p.name,
                    "image_url": p.image_url,
                    "sub_category": p.sub_category,
                    "figure_id": p.figure_id
                }
                if p.ean in ean_map:
                    ean_map[p.ean].append(product_info)
                else:
                    ean_map[p.ean] = [product_info]
        
        for ean, prods in ean_map.items():
            if len(prods) > 1:
                duplicates.append({
                    "reason": f"EAN compartido: {ean}",
                    "products": prods
                })
        
        return duplicates

@app.post("/api/admin/nexus/sync", dependencies=[Depends(verify_api_key)])
async def sync_nexus(background_tasks: BackgroundTasks):
    """
    Dispara la sincronización manual del catálogo maestro de ActionFigure411.
    """
    try:
        from src.application.services.nexus_service import NexusService
        
        # Lo ejecutamos en segundo plano para no bloquear la UI
        background_tasks.add_task(NexusService.sync_catalog)
        
        return {"status": "success", "message": "Iniciando sincronización del Nexo Maestro en segundo plano..."}
    except Exception as e:
        logger.error(f"Failed to start Nexus sync: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"No se pudo iniciar Nexus: {str(e)}")

@app.post("/api/products/merge", dependencies=[Depends(verify_api_key)])
async def merge_products(request: ProductMergeRequest):
    """
    Fusiona dos productos. Transfiere ofertas y colecciones al target y borra el source.
    """
    with SessionCloud() as db:
        source = db.query(ProductModel).filter(ProductModel.id == request.source_id).first()
        target = db.query(ProductModel).filter(ProductModel.id == request.target_id).first()
        if not source or not target: raise HTTPException(status_code=404, detail="Producto(s) no encontrado")
            
        # 1. Transferir ofertas
        db.query(OfferModel).filter(OfferModel.product_id == source.id).update({"product_id": target.id})
        
        # 2. Transferir coleccionistas
        source_items = db.query(CollectionItemModel).filter(CollectionItemModel.product_id == source.id).all()
        for item in source_items:
            exists = db.query(CollectionItemModel).filter(
                CollectionItemModel.product_id == target.id,
                CollectionItemModel.owner_id == item.owner_id
            ).first()
            if not exists:
                item.product_id = target.id
            else:
                db.delete(item)
                
        # 3. Eliminar fuente
        source_name = source.name
        db.delete(source)
        db.commit()
        return {"status": "success", "message": f"Fusión divina: '{source_name}' ha sido absorbido por '{target.name}'"}

@app.get("/api/guardian/export/excel")
async def export_excel(user_id: int = 1): # Hardcoded David for now, should use Auth dependency
    """
    Genera y sirve el Excel Maestro sincronizado con la colección del usuario.
    """
    try:
        from src.application.services.guardian_service import GuardianService
        with SessionCloud() as db:
            file_path = GuardianService.export_collection_to_excel(db, user_id)
            
        if not os.path.exists(file_path):
             raise HTTPException(status_code=500, detail="Error al generar el archivo Excel")
             
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Excel Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guardian/export/sqlite")
async def export_sqlite(user_id: int = 1):
    """
    Genera y sirve la Bóveda SQLite (Bunker Físico).
    """
    try:
        from src.application.services.guardian_service import GuardianService
        with SessionCloud() as db:
            file_path = GuardianService.export_collection_to_sqlite(db, user_id)
            
        if not os.path.exists(file_path):
             raise HTTPException(status_code=500, detail="Error al generar la Bóveda SQLite")
             
        return FileResponse(
            path=file_path, 
            filename=os.path.basename(file_path),
            media_type='application/x-sqlite3'
        )
    except Exception as e:
        logger.error(f"SQLite Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collection/toggle")
async def toggle_collection(request: CollectionToggleRequest):
    """
    Añade o elimina un producto de la colección del usuario (o lista de deseos).
    """
    from src.domain.models import CollectionItemModel
    with SessionCloud() as db:
        # Buscar si ya existe
        item = db.query(CollectionItemModel).filter(
            CollectionItemModel.product_id == request.product_id,
            CollectionItemModel.owner_id == request.user_id
        ).first()

        if item:
            # Caso 1: Estaba en deseos y ahora lo marcamos como poseído (Upgrade)
            if not item.acquired and not request.wish:
                item.acquired = True
                action = "upgraded"
            # Caso 2: Estaba poseído y ahora lo marcamos como deseos (Downgrade - opcional, por ahora tratamos como toggle normal)
            # Por simplicidad, si ya existe y pulsas lo mismo, se borra (toggle off)
            else:
                db.delete(item)
                action = "removed"
        else:
            # Crear según el tipo solicitado
            new_item = CollectionItemModel(
                product_id=request.product_id,
                owner_id=request.user_id,
                acquired=not request.wish
            )
            db.add(new_item)
            action = "added_wish" if request.wish else "added_owned"
        
        db.commit()
        return {"status": "success", "action": action, "product_id": request.product_id}

@app.patch("/api/collection/{product_id}")
async def update_collection_item(product_id: int, request: CollectionItemUpdateRequest):
    """
    Actualiza los detalles privados de un item de la colección (Legado).
    """
    with SessionCloud() as db:
        item = db.query(CollectionItemModel).filter(
            CollectionItemModel.product_id == product_id,
            CollectionItemModel.owner_id == request.user_id
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado en tu colección")
        
        if request.condition is not None: item.condition = request.condition
        if request.grading is not None: item.grading = request.grading
        if request.purchase_price is not None: item.purchase_price = request.purchase_price
        if request.notes is not None: item.notes = request.notes
        if request.acquired_at is not None:
            try:
                # Handle possible 'Z' or offset if any, usually from JS isoString
                clean_date = request.acquired_at.replace('Z', '')
                item.acquired_at = datetime.fromisoformat(clean_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido")
        
        db.commit()
        return {"status": "success", "message": "Detalles del legado actualizados"}

# --- PURGATORY ENDPOINTS ---

@app.get("/api/purgatory", dependencies=[Depends(verify_api_key)])
async def get_purgatory(page: int = 1, limit: int = 500):
    """
    Retorna items en el Purgatorio con SUGERENCIAS INTELIGENTES.
    Cada item incluye una lista de posibles productos match con su score de confianza.
    """
    from src.core.brain_engine import engine
    from sqlalchemy import select
    
    with SessionCloud() as db:
        # Paginación básica para evitar cuelgues de red/memoria
        offset = (page - 1) * limit
        pending = db.query(PendingMatchModel).order_by(desc(PendingMatchModel.found_at)).offset(offset).limit(limit).all()
        products = db.query(ProductModel).all()
        
        results = []
        for item in pending:
            try:
                # Pre-calcular tokens de búsqueda para el item actual
                suggestions = []
                # Fallback seguro para nombres nulos
                scraped_name_safe = (item.scraped_name or "").lower()
                
                search_tokens = set(re.findall(r'\w+', scraped_name_safe))
                # Ignorar palabras genéricas comunes
                search_tokens -= {"masters", "of", "the", "universe", "origins", "motu"}
                
                for p in products:
                    # OPTIMIZACIÓN: Solo calcular match real si hay alguna coincidencia de palabras clave
                    # o si tienen el mismo EAN (match directo)
                    p_name_lower = (p.name or "").lower()
                    has_keyword = any(token in p_name_lower for token in search_tokens) if search_tokens else True
                    
                    if has_keyword or (p.ean and p.ean == item.ean):
                        # Usamos el engine para calcular el score fino
                        _, score, reason = engine.calculate_match(p.name, item.scraped_name, p.ean, item.ean)
                        
                        if score > 0.30:
                            suggestions.append({
                                "product_id": p.id,
                                "name": p.name,
                                "figure_id": p.figure_id,
                                "sub_category": p.sub_category,
                                "match_score": round(score * 100, 1),
                                "reason": reason
                            })
                
                # Ordenar sugerencias por score descendente
                suggestions.sort(key=lambda x: x["match_score"], reverse=True)
                
                item_dict = {
                    "id": item.id,
                    "scraped_name": item.scraped_name,
                    "ean": item.ean,
                    "price": item.price,
                    "currency": item.currency,
                    "url": item.url,
                    "shop_name": item.shop_name,
                    "image_url": item.image_url,
                    "found_at": item.found_at,
                    "source_type": item.source_type,
                    "validation_status": item.validation_status,
                    "is_blocked": item.is_blocked,
                    "opportunity_score": item.opportunity_score,
                    "anomaly_flags": json.loads(item.anomaly_flags) if item.anomaly_flags else [],
                    "suggestions": suggestions[:5] # Top 5 sugerencias
                }
                results.append(item_dict)
            except Exception as e:
                logger.error(f"Error procesando item {getattr(item, 'id', 'unknown')} en Purgatorio: {e}")
                # No añadir nada a results para este item fallido o añadir un placeholder seguro
                continue
            
        return results

@app.post("/api/admin/validate-anomaly", dependencies=[Depends(verify_api_key)])
async def validate_anomaly(request: AnomalyValidationRequest):
    """
    Permite al Arquitecto validar o bloquear definitivamente un item con anomalías.
    """
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado en el Purgatorio")
        
        if request.action == "validate":
            item.validation_status = "VALIDATED"
            item.is_blocked = False
            item.anomaly_flags = None
            message = "Anomalía aceptada por el Arquitecto. Item desbloqueado."
        else:
            item.validation_status = "REJECTED"
            item.is_blocked = True
            message = "Item bloqueado definitivamente."
            
        db.commit()
        return {"status": "success", "message": message}

# --- ADMIN / DATA PURIFICATION ENDPOINTS ---

@app.post("/api/admin/reset-smartmatches", dependencies=[Depends(verify_api_key)])
async def reset_smartmatches():
    """
    PURIFICACIÓN TOTAL: Desvincula TODAS las ofertas activas.
    Las devuelve al Purgatorio para revisión manual del Maestro con el nuevo umbral del 75%.
    """
    import json
    
    with SessionCloud() as db:
        # Obtener TODAS las ofertas vinculadas (con product_id)
        all_offers = db.query(OfferModel).filter(OfferModel.product_id.isnot(None)).all()
        
        reverted_count = 0
        for offer in all_offers:
            # Evitar duplicados en Purgatorio
            exists = db.query(PendingMatchModel).filter(PendingMatchModel.url == offer.url).first()
            if not exists:
                # Obtener nombre del producto para el Purgatorio
                product_name = offer.product.name if offer.product else "Unknown"
                
                pending = PendingMatchModel(
                    scraped_name=product_name,
                    price=offer.price,
                    currency=offer.currency,
                    url=offer.url,
                    shop_name=offer.shop_name,
                    image_url=None
                )
                db.add(pending)
            
            # Eliminar la oferta vinculada
            db.delete(offer)
            reverted_count += 1
            
        db.commit()
        return {
            "status": "success", 
            "message": f"Purificación TOTAL completada. {reverted_count} ofertas devueltas al Purgatorio."
        }

@app.post("/api/purgatory/match", dependencies=[Depends(verify_api_key)])
async def match_purgatory(request: PurgatoryMatchRequest):
    """Vincula un item del Purgatorio con un Producto existente y registra el evento con datos completos"""
    from src.domain.models import OfferHistoryModel
    from sqlalchemy.exc import IntegrityError
    
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
        
        # Idempotencia: Si el item ya no está en Purgatorio, comprobamos si ya se vinculó
        if not item:
            # Podría haber sido procesado por otra pestaña o una ejecución previa
            existing_offer = db.query(OfferModel).filter(OfferModel.product_id == request.product_id).first() # Una simplificación
            if existing_offer:
                return {"status": "success", "message": "Reliquia ya procesada previamente (Idempotencia)"}
            raise HTTPException(status_code=404, detail="Reliquia no encontrada en el Purgatorio")
            
        if not product:
            raise HTTPException(status_code=404, detail="Producto objetivo no encontrado")
        
        try:
            # 1. Usar el repositorio para añadir la oferta (Garantiza Phase 41 + Phase 39)
            from src.infrastructure.repositories.product import ProductRepository
            repo = ProductRepository(db)
            
            # PHASE 42: Fresh Opportunity Score Calculation
            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == 1).first() # Default user
            if user: user_location = user.location
            
            landed_p = LogisticsService.get_landing_price(item.price, item.shop_name, user_location)
            is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in product.collection_items)
            fresh_score = DealScorer.calculate_score(product, landed_p, is_wish)

            offer_data = {
                "shop_name": item.shop_name,
                "price": item.price,
                "currency": item.currency,
                "url": item.url,
                "is_available": True,
                "source_type": item.source_type,
                "receipt_id": item.receipt_id,
                "opportunity_score": fresh_score,
                # Phase 41 Metadata
                "first_seen_at": item.found_at,
                "last_price_update": datetime.utcnow()
            }
            
            new_offer, _ = repo.add_offer(product, offer_data, commit=False)

            # 2. Registrar historial
            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=product.name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="LINKED_MANUAL",
                details=json.dumps({"product_id": product.id, "receipt_id": item.receipt_id})
            )
            db.add(history)
            
            # 3. Crear Alias
            from src.domain.models import ProductAliasModel
            db.query(ProductAliasModel).filter(ProductAliasModel.source_url == item.url).delete()
            new_alias = ProductAliasModel(
                product_id=product.id,
                source_url=item.url,
                confirmed=True
            )
            db.add(new_alias)
            
            # 4. Limpiar Purgatorio
            db.delete(item)
            db.commit()
            return {"status": "success", "message": "Vínculo sagrado establecido para la posteridad"}
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad en match_purgatory: {e}")
            raise HTTPException(status_code=409, detail="Error de integridad: Posible duplicidad de URL o Producto")
        except Exception as e:
            db.rollback()
            logger.error(f"Error inesperado en match_purgatory: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/purgatory/discard", dependencies=[Depends(verify_api_key)])
async def discard_purgatory(request: PurgatoryDiscardRequest):
    """Descarta un item del Purgatorio, lo añade a la lista negra y registra la acción"""
    from src.domain.models import OfferHistoryModel
    from sqlalchemy.exc import IntegrityError
    
    with SessionCloud() as db:
        item = db.query(PendingMatchModel).filter(PendingMatchModel.id == request.pending_id).first()
        
        # Idempotencia
        if not item:
            # Quizás ya fue descartado
            return {"status": "success", "message": "Reliquia ya procesada o inexistente (Idempotencia)"}
        
        try:
            # Guardar copia de los datos originales
            item_data = {
                "scraped_name": item.scraped_name,
                "ean": item.ean,
                "price": item.price,
                "currency": item.currency,
                "url": item.url,
                "shop_name": item.shop_name,
                "image_url": item.image_url,
                "receipt_id": item.receipt_id
            }

            # 1. Añadir a Lista Negra (Evitando duplicados explícitamente)
            exists = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == item.url).first()
            if not exists:
                bl = BlackcludedItemModel(
                    url=item.url,
                    scraped_name=item.scraped_name,
                    reason=request.reason,
                    source_type=item.source_type
                )
                db.add(bl)

            # 2. Registrar en historial
            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=item.scraped_name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="DISCARDED_MANUAL",
                details=json.dumps({"reason": request.reason, "original_item": item_data})
            )
            db.add(history)

            # 3. Limpiar Purgatorio
            db.delete(item)
            db.commit()
            return {"status": "success", "message": "Item enviado a las sombras de la lista negra"}
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error de integridad en discard_purgatory: {e}")
            # Si ya existía en lista negra pero no lo detectó el select anterior, simplemente limpiamos purgatorio
            db.delete(item)
            db.commit()
            return {"status": "success", "message": "Item ya estaba en lista negra, purificado del Purgatorio"}
        except Exception as e:
            db.rollback()
            logger.error(f"Error inesperado en discard_purgatory: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/purgatory/discard/bulk", dependencies=[Depends(verify_api_key)])
async def discard_purgatory_bulk(request: PurgatoryBulkDiscardRequest):
    """
    Descarta múltiples items del Purgatorio a la vez.
    """
    with SessionCloud() as db:
        items = db.query(PendingMatchModel).filter(PendingMatchModel.id.in_(request.pending_ids)).all()
        count = 0
        for item in items:
            # Evitar duplicados en lista negra
            exists = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == item.url).first()
            if not exists:
                blacklist = BlackcludedItemModel(
                    url=item.url,
                    scraped_name=item.scraped_name,
                    reason=request.reason
                )
                db.add(blacklist)
            
            # Registrar historial de descarte masivo para cada uno
            history = OfferHistoryModel(
                offer_url=item.url,
                product_name=item.scraped_name,
                shop_name=item.shop_name,
                price=item.price,
                action_type="DISCARDED_BULK",
                details=json.dumps({"reason": request.reason})
            )
            db.add(history)
            
            db.delete(item)
            count += 1
        
        db.commit()
    
    return {"status": "success", "message": f"{count} items desterrados al abismo."}

# --- SCRAPER CONTROL ENDPOINTS movidos a routers/scrapers.py ---
# (run_scraper_task, scraper_cancel_event, /api/scrapers/status, /api/scrapers/logs,
#  /api/scrapers/run, /api/scrapers/stop)


@app.get("/api/dashboard/stats", dependencies=[Depends(verify_device)])
async def get_dashboard_stats(user_id: int = 1):
    """
    Retorna métricas globales para el Tablero de Inteligencia, filtradas por usuario.
    Diferencia entre items poseídos y lista de deseos.
    """
    try:
        from sqlalchemy import func
        with SessionCloud() as db:
            total_products = db.query(ProductModel).count()
            # Solo contamos items poseídos (acquired=True) para las métricas de "Poder"
            owned_count = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id, 
                CollectionItemModel.acquired == True
            ).count()
            
            wish_count = db.query(CollectionItemModel).filter(
                CollectionItemModel.owner_id == user_id, 
                CollectionItemModel.acquired == False
            ).count()

            # --- FINANCIAL ENGINE (CENTRALIZED WATERFALL) ---
            from src.application.services.valuation_service import ValuationService
            
            valuation_service = ValuationService(db)
            user_location = "ES"
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user: user_location = user.location
            
            financials = valuation_service.get_collection_valuation(user_id, user_location)
            
            total_invested = financials["total_invested"]
            market_value = financials["total_value"]
            landed_market_value = financials["landed_market_value"] # Phase 15.2
            profit_loss = financials["profit_loss"]
            roi = financials["roi"]

            # Distribución por tienda (Global Retail para inteligencia de mercado)
            shop_dist = db.query(OfferModel.shop_name, func.count(OfferModel.id))\
                .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True, OfferModel.source_type == 'Retail')\
                .group_by(OfferModel.shop_name)\
                .all()
            
            match_count = sum(count for _, count in shop_dist)
            
            return {
                "total_products": total_products,
                "owned_count": owned_count,
                "wish_count": wish_count,
                "financial": {
                    "total_invested": round(total_invested, 2),
                    "market_value": round(market_value, 2),
                    # "landed_market_value": round(landed_market_value, 2), # Desactivado por petición (Fase 42)
                    "profit_loss": round(profit_loss, 2),
                    "roi": round(roi, 1)
                },
                "match_count": match_count,
                "shop_distribution": [{"shop": s, "count": c} for s, c in shop_dist]
            }
    except Exception as e:
        logger.error(f"CRITICAL DASHBOARD ERROR for user {user_id}: {e}")
        # Phase 15: Don't return null, return an error so the frontend can react
        raise HTTPException(
            status_code=500, 
            detail=f"Error al recuperar datos del tablero: {str(e)}"
        )
        return {
            "total_products": 0, "owned_count": 0, "wish_count": 0,
            "financial": {"total_invested": 0, "market_value": 0, "profit_loss": 0, "roi": 0},
            "match_count": 0, "shop_distribution": []
        }

@app.get("/api/products/with-offers", dependencies=[Depends(verify_device)])
async def get_products_with_offers():
    """
    Retorna una lista de IDs de productos que tienen ofertas activas vinculadas.
    Usado para indicar visualmente qué productos tienen inteligencia de mercado.
    """
    with SessionCloud() as db:
        product_ids = db.query(OfferModel.product_id)\
            .filter(OfferModel.product_id.isnot(None), OfferModel.is_available == True)\
            .distinct()\
            .all()
        return [p[0] for p in product_ids]

@app.get("/api/products/{product_id}/offers", dependencies=[Depends(verify_device)])
async def get_product_offers(product_id: int):
    """
    Retorna la mejor oferta actual por TIENDA para un producto.
    Solo muestra la ÚLTIMA oferta válida de cada tienda, destacando la mejor global.
    """
    from sqlalchemy import desc
    with SessionCloud() as db:
        # Obtenemos TODAS las ofertas activas, ordenadas por precio asc y luego por fecha desc
        # NOTA: En una query más compleja haríamos un DISTINCT ON (shop_name) en Postgres,
        # para SQLite lo agrupamos en Python para asegurar 'La Verdad del Oráculo'.
        all_offers = db.query(OfferModel)\
            .filter(OfferModel.product_id == product_id, OfferModel.is_available == True)\
            .order_by(OfferModel.price.asc(), desc(OfferModel.last_seen))\
            .all()
            
        # Agrupación por tienda
        # Get user location for logistics
        user_location = "ES"
        # We assume user_id 1 for now or inject it
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user: user_location = user.location

        latest_by_shop = {}
        for o in all_offers:
            if o.shop_name not in latest_by_shop:
                landing_p = LogisticsService.get_landing_price(o.price, o.shop_name, user_location)
                latest_by_shop[o.shop_name] = {
                    "id": o.id,
                    "shop_name": o.shop_name,
                    "price": o.price,
                    "landing_price": landing_p,
                    "url": o.url,
                    "last_seen": o.last_seen.isoformat(),
                    "min_historical": o.min_price or o.price,
                    "opportunity_score": o.opportunity_score,
                    "source_type": o.source_type,
                    "is_best": False,
                    "is_available": o.is_available,
                    # Phase 39: Auction Intelligence
                    "sale_type": o.sale_type,
                    "expiry_at": o.expiry_at.isoformat() if o.expiry_at else None,
                    "bids_count": o.bids_count,
                    "time_left_raw": o.time_left_raw
                }
        
        # Marcar la mejor global basada en Landing Price (Phase 15 Truth)
        results = list(latest_by_shop.values())
        if results:
            results.sort(key=lambda x: x["landing_price"])
            results[0]["is_best"] = True
            
        return results

@app.get("/api/market/analytics/{product_id}")
async def get_market_analytics(product_id: int):
    """
    Fase 40: Estudio de mercado avanzado.
    Separa estadísticas entre Retail (Tiendas) y P2P (Subastas/Particulares).
    """
    with SessionCloud() as db:
        offers = db.query(OfferModel).filter(
            OfferModel.product_id == product_id, 
            OfferModel.is_available == True
        ).all()
        
        retail_prices = [o.price for o in offers if o.source_type == "Retail"]
        p2p_prices = [o.price for o in offers if o.source_type == "Peer-to-Peer"]
        
        # Stats Helpers
        def get_stats(prices):
            if not prices: return {"avg": 0, "min": 0, "max": 0, "count": 0}
            return {
                "avg": round(sum(prices) / len(prices), 2),
                "min": min(prices),
                "max": max(prices),
                "count": len(prices)
            }
            
        return {
            "retail": get_stats(retail_prices),
            "p2p": get_stats(p2p_prices),
            "global_avg": get_stats(retail_prices + p2p_prices)["avg"]
        }

@app.get("/api/products/{product_id}/price-history")
async def get_product_price_history(product_id: int):
    """
    Retorna la evolución de precios de un producto agrupada por tienda.
    Fase 44: Consolidación por ShopName y eliminación de duplicados diarios.
    """
    from src.domain.models import OfferModel, PriceHistoryModel
    from collections import defaultdict
    
    with SessionCloud() as db:
        # Buscamos todas las ofertas vinculadas a este producto (activas o no)
        offers = db.query(OfferModel).filter(OfferModel.product_id == product_id).all()
        
        # Agrupamos historial por tienda
        shop_groups = defaultdict(list)
        
        for offer in offers:
            history = db.query(PriceHistoryModel)\
                .filter(PriceHistoryModel.offer_id == offer.id)\
                .order_by(PriceHistoryModel.recorded_at.asc())\
                .all()
            
            for h in history:
                date_key = h.recorded_at.date().isoformat()
                shop_groups[offer.shop_name].append({
                    "date": date_key,
                    "price": h.price,
                    "timestamp": h.recorded_at
                })
        
        results = []
        for shop_name, history_points in shop_groups.items():
            # Consolidamos por día: si hay varios registros el mismo día, tomamos el mínimo (Mejor oferta)
            daily_best = {}
            for p in history_points:
                date = p["date"]
                if date not in daily_best or p["price"] < daily_best[date]["price"]:
                    daily_best[date] = p
            
            # Ordenamos por fecha
            sorted_history = sorted(daily_best.values(), key=lambda x: x["timestamp"])
            
            results.append({
                "shop_name": shop_name,
                "history": [
                    {
                        "date": p["date"],
                        "price": p["price"]
                    } for p in sorted_history
                ]
            })
        
        # Ordenamos resultados por nombre de tienda para consistencia en el frontend
        results.sort(key=lambda x: x["shop_name"])
        return results

@app.get("/api/dashboard/hall-of-fame", dependencies=[Depends(verify_device)])
async def get_dashboard_hall_of_fame(user_id: int = 1):
    """
    Fase 6.3: Retorna los 'Griales del Reino' (Top Valor) y 'Potencial Oculto' (Top ROI).
    """
    from src.domain.models import CollectionItemModel, OfferModel, ProductModel
    
    with SessionCloud() as db:
        # 1. Obtener todos los items de colección filtrados por el usuario
        items = (
            db.query(CollectionItemModel)
            .join(ProductModel)
            .filter(CollectionItemModel.acquired == True, CollectionItemModel.owner_id == user_id)
            .all()
        )
        
        if not items:
            return {"top_value": [], "top_roi": []}
            
        from src.application.services.valuation_service import ValuationService
        valuation_service = ValuationService(db)
        
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user: user_location = user.location

        analyzed_items = []
        for item in items:
            market_val = valuation_service.get_consolidated_value(item.product, user_location)
            invested = item.purchase_price or 0.0
            
            roi = 0.0
            if invested > 0:
                roi = ((market_val - invested) / invested) * 100

            analyzed_items.append({
                "id": item.product.id,
                "name": item.product.name,
                "image_url": item.product.image_url,
                "figure_id": item.product.figure_id,
                "market_value": round(market_val, 2),
                "purchase_price": invested,
                "roi": round(roi, 1)
            })
        
        # 4. Sorting & Response
        top_value = sorted(analyzed_items, key=lambda x: x["market_value"], reverse=True)[:5]
        top_roi = sorted(analyzed_items, key=lambda x: x["roi"], reverse=True)[:5]
        
        return {
            "top_value": top_value,
            "top_roi": [i for i in top_roi if i["roi"] > 0] # Solo mostrar los que tienen ROI positivo
        }

@app.get("/api/dashboard/top-deals", dependencies=[Depends(verify_device)])
async def get_top_deals(user_id: int = 2):
    """
    Retorna las 20 mejores ofertas actuales de items NO CAPTURADOS.
    MEJORA: Solo muestra el mejor precio por producto (sin duplicados).
    """
    from sqlalchemy import func, and_
    
    with SessionCloud() as db:
        # 1. Obtenemos IDs de productos ya capturados (adquiridos) por el usuario
        owned_ids = [p[0] for p in db.query(CollectionItemModel.product_id).filter(
            CollectionItemModel.owner_id == user_id,
            CollectionItemModel.acquired == True
        ).all()]

        # 2. Subquery: Encontrar el precio mínimo para cada producto disponible (RETAIL)
        from datetime import datetime, timedelta
        freshness_threshold = datetime.utcnow() - timedelta(hours=72)
        
        best_prices_subq = db.query(
            OfferModel.product_id,
            func.min(OfferModel.price).label('min_price')
        ).filter(
            OfferModel.is_available == True,
            OfferModel.last_seen >= freshness_threshold, # Solo stock real detectado recientemente
            OfferModel.source_type == 'Retail',
            OfferModel.product_id.notin_(owned_ids) if owned_ids else True
        ).group_by(OfferModel.product_id).subquery()

        # 3. Join para obtener los detalles de la oferta más barata por producto
        offers = db.query(OfferModel).join(
            best_prices_subq,
            and_(
                OfferModel.product_id == best_prices_subq.c.product_id,
                OfferModel.price == best_prices_subq.c.min_price
            )
        ).join(ProductModel).filter(
            OfferModel.is_available == True,
            OfferModel.last_seen >= freshness_threshold, # Doble check de frescura
            OfferModel.opportunity_score > 0             # Solo gangas reales (>0)
        ).order_by(OfferModel.opportunity_score.desc()) # Priorizar por calidad de oferta
        # 4. Construir respuesta con Landing Price (OPTIMIZADO)
        # Pre-cargar Reglas Logísticas para evitar N+1
        rules = db.query(LogisticRuleModel).all()
        rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}

        # Get user location for logistics
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user: user_location = user.location

        offers_pool = offers.limit(50).all() # Pool más grande para re-ordenar
        
        results = []
        for o in offers_pool:
            landing_p = LogisticsService.optimized_get_landing_price(o.price, o.shop_name, user_location, rules_map)
            results.append({
                "id": o.id,
                "product_name": o.product.name,
                "price": o.price,
                "landing_price": landing_p,
                "shop_name": o.shop_name,
                "url": o.url,
                "opportunity_score": o.opportunity_score,
                "image_url": o.product.image_url
            })
        
        # 5. Re-ordenar por Landing Price (La Verdad Definitiva)
        results.sort(key=lambda x: x["landing_price"])
        
        # 6. Deduplicar por nombre de producto para variedad
        seen_names = set()
        final_deals = []
        for r in results:
            if r["product_name"] not in seen_names:
                seen_names.add(r["product_name"])
                final_deals.append(r)
                
        return final_deals[:20]

@app.get("/api/radar/p2p-opportunities")
async def get_p2p_opportunities(user_id: int = 2):
    """
    Fase 16: Radar de Oportunidades Particulares (Wallapop/eBay).
    Muestra ofertas de particulares que están por debajo del percentil 25 histórico.
    """
    with SessionCloud() as db:
        # Get user location for logistics
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user: user_location = user.location

        # Query Peer-to-Peer offers where price <= product.p25_price
        # We also want p25_price > 0 (to avoid items without benchmark data)
        opportunities = db.query(OfferModel).join(ProductModel).filter(
            OfferModel.is_available == True,
            OfferModel.source_type == 'Peer-to-Peer',
            ProductModel.p25_price > 0,
            OfferModel.price <= ProductModel.p25_price
        ).all()

        results = []
        for o in opportunities:
            # ROI de Oportunidad: Cuánto ahorras respecto al p25_price
            saving = o.product.p25_price - o.price
            saving_pct = (saving / o.product.p25_price * 100) if o.product.p25_price > 0 else 0.0

            results.append({
                "id": o.id,
                "product_name": o.product.name,
                "ean": o.product.ean,
                "image_url": o.product.image_url,
                "price": o.price,
                "p25_price": o.product.p25_price,
                "avg_market_price": o.product.avg_market_price,
                "saving": round(saving, 2),
                "saving_pct": round(saving_pct, 1),
                "shop_name": o.shop_name,
                "url": o.url,
                "opportunity_score": o.opportunity_score,
                "landing_price": LogisticsService.get_landing_price(o.price, o.shop_name, user_location)
            })
        
        # Ordenar por el mayor porcentaje de ahorro
        return sorted(results, key=lambda x: x["saving_pct"], reverse=True)

@app.get("/api/dashboard/match-stats")
async def get_dashboard_match_stats():
    """Retorna estadísticas de conquistas ACTUALES por tienda (enlaces activos)"""
    from sqlalchemy import func
    with SessionCloud() as db:
        stats = db.query(
            OfferModel.shop_name.label("shop"), 
            func.count(OfferModel.id).label("count")
        ).filter(
            OfferModel.product_id.isnot(None),
            OfferModel.is_available == True
        ).group_by(
            OfferModel.shop_name
        ).all()
        
        return [{"shop": s.shop, "count": s.count} for s in stats]

@app.get("/api/dashboard/history")
async def get_dashboard_history():
    """Retorna los movimientos recientes de almas (vínculos/descartes)"""
    from sqlalchemy import desc
    from src.domain.models import OfferHistoryModel
    with SessionCloud() as db:
        history = db.query(OfferHistoryModel)\
            .order_by(desc(OfferHistoryModel.timestamp))\
            .limit(10)\
            .all()
            
        return [{
            "id": h.id,
            "product_name": h.product_name,
            "shop_name": h.shop_name,
            "price": h.price,
            "action_type": h.action_type,
            "timestamp": h.timestamp.isoformat(),
            "offer_url": h.offer_url
        } for h in history]

@app.post("/api/dashboard/revert")
async def revert_action(request: dict):
    """Revierte una acción de vínculo o descarte, con soporte para reconstrucción retroactiva"""
    history_id = request.get("history_id")
    if not history_id:
        raise HTTPException(status_code=400, detail="ID de historial requerido")
        
    with SessionCloud() as db:
        history = db.query(OfferHistoryModel).filter(OfferHistoryModel.id == history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="Entrada de historial no encontrada")
            
        # Intentar obtener metadatos completos
        original_item = None
        try:
            details_json = json.loads(history.details)
            # El JSON puede ser {"original_item": {...}} o un formato anterior
            if isinstance(details_json, dict):
                 original_item = details_json.get("original_item")
        except:
            # Fallback retroactivo: No hay JSON, usamos campos base de la tabla history
            logger.warning(f"Reconstruction Fallback for History ID {history_id}: No JSON metadata found.")

        # Si no hay metadatos guardados, usamos lo mínimo disponible en las columnas
        if not original_item:
            original_item = {
                "scraped_name": history.product_name,
                "ean": None,
                "price": history.price,
                "currency": "EUR",
                "url": history.offer_url,
                "shop_name": history.shop_name,
                "image_url": None,
                "receipt_id": None
            }
            
        # Lógica de limpieza según el tipo de acción
        if history.action_type in ["LINKED_MANUAL", "SMART_MATCH", "UPDATE"]:
            # Borrar la oferta del catálogo para que el item "vuelva" a ser una oportunidad nueva
            offer = db.query(OfferModel).filter(OfferModel.url == history.offer_url).first()
            if offer:
                db.delete(offer)
        
        elif history.action_type == "DISCARDED":
            # Borrar de la lista negra
            bl = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == history.offer_url).first()
            if bl:
                db.delete(bl)
        
        # Recrear el item en el Purgatorio
        purgatory_item = PendingMatchModel(
            scraped_name=original_item["scraped_name"],
            ean=original_item.get("ean"),
            price=original_item["price"],
            currency=original_item.get("currency", "EUR"),
            url=original_item["url"],
            shop_name=original_item["shop_name"],
            image_url=original_item.get("image_url"),
            receipt_id=original_item.get("receipt_id")
        )
        db.add(purgatory_item)
        
        # Eliminar la entrada de historial para evitar duplicidad de reversión
        db.delete(history)
        db.commit()
        
        return {"status": "success", "message": f"Justicia restaurada: '{history.product_name}' devuelto al Purgatorio"}

@app.post("/api/offers/{offer_id}/unlink", dependencies=[Depends(verify_api_key)])
async def unlink_offer(offer_id: int):
    """
    Desvincula una oferta de su producto y la devuelve al Purgatorio.
    (Admin Only)
    """
    from src.domain.models import ProductAliasModel
    with SessionCloud() as db:
        offer = db.query(OfferModel).filter(OfferModel.id == offer_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        product_name = offer.product.name if offer.product else "Reliquia Desconocida"

        # 1. Crear item en Purgatorio
        purgatory_item = PendingMatchModel(
            scraped_name=product_name,
            ean=None, 
            price=offer.price,
            currency=offer.currency,
            url=offer.url,
            shop_name=offer.shop_name,
            image_url=None,
            source_type=offer.source_type
        )
        db.add(purgatory_item)

        # 2. Registrar historial
        history = OfferHistoryModel(
            offer_url=offer.url,
            product_name=product_name,
            shop_name=offer.shop_name,
            price=offer.price,
            action_type="UNLINKED_MANUAL_ADMIN",
            details=json.dumps({"reason": "Desvinculación manual por el Arquitecto"})
        )
        db.add(history)

        # 3. Eliminar Alias (para evitar que el SmartMatch lo re-vincule automáticamente)
        db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()

        # 4. Eliminar oferta vinculada
        db.delete(offer)

        db.commit()
        return {"status": "success", "message": f"Justicia del Arquitecto: '{product_name}' ha sido devuelto al Purgatorio"}

@app.post("/api/offers/{offer_id}/relink", dependencies=[Depends(verify_api_key)])
async def relink_offer(offer_id: int, request: RelinkOfferRequest):
    """
    Desvincula una oferta de su producto actual y la vincula a uno nuevo.
    (Admin Only)
    """
    from src.domain.models import ProductAliasModel
    with SessionCloud() as db:
        offer = db.query(OfferModel).filter(OfferModel.id == offer_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")

        old_product_name = offer.product.name if offer.product else "Desconocido"
        new_product = db.query(ProductModel).filter(ProductModel.id == request.target_product_id).first()
        if not new_product:
            raise HTTPException(status_code=404, detail="Producto destino no encontrado")

        # 1. Actualizar vinculo
        offer.product_id = new_product.id

        # PHASE 42: Recalculate Score for new product benchmark
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user: user_location = user.location
        
        landed_p = LogisticsService.get_landing_price(offer.price, offer.shop_name, user_location)
        is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in new_product.collection_items)
        offer.opportunity_score = DealScorer.calculate_score(new_product, landed_p, is_wish)
        
        # 2. Actualizar/Crear Alias
        # Eliminamos el viejo y creamos el nuevo para asegurar limpieza
        db.query(ProductAliasModel).filter(ProductAliasModel.source_url == offer.url).delete()
        new_alias = ProductAliasModel(
            product_id=new_product.id,
            source_url=offer.url,
            confirmed=True
        )
        db.add(new_alias)

        # 3. Registrar historial
        history = OfferHistoryModel(
            offer_url=offer.url,
            product_name=new_product.name,
            shop_name=offer.shop_name,
            price=offer.price,
            action_type="RELINKED_MANUAL_ADMIN",
            details=json.dumps({
                "from_product": old_product_name,
                "to_product": new_product.name,
                "reason": "Redirección manual por el Arquitecto"
            })
        )
        db.add(history)

        db.commit()
        return {"status": "success", "message": f"Decreto del Arquitecto: Oferta reasignada a '{new_product.name}'"}

@app.post("/api/wallapop/import")
async def import_wallapop_products(request: WallapopImportRequest):
    """
    Recibe productos de Wallapop desde la extensión de Chrome
    y los guarda en el Purgatorio para revisión manual.
    """
    imported = 0
    
    with SessionCloud() as db:
        for product in request.products:
            # Verificar si ya existe
            existing = db.query(PendingMatchModel).filter(
                PendingMatchModel.url == product.url
            ).first()
            
            if existing:
                continue
            
            # Crear item en Purgatorio
            pending = PendingMatchModel(
                scraped_name=f"[Wallapop] {product.title}",
                price=product.price,
                currency="EUR",
                url=product.url,
                shop_name="Wallapop",
                source_type="Peer-to-Peer", # Fase 16: ADN P2P
                image_url=product.imageUrl,
                found_at=datetime.utcnow()
            )
            db.add(pending)
            imported += 1
        
        db.commit()
    
    logger.info(f"[Wallapop Extension] Importados {imported} productos al Purgatorio")
    return {"status": "success", "imported": imported, "total_received": len(request.products)}

@app.get("/api/users/{user_id}", dependencies=[Depends(verify_device)])
async def get_user_settings(user_id: int):
    """
    Fase 15: Obtiene la configuración del usuario.
    """
    from src.domain.models import UserModel
    
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "location": user.location,
            "role": user.role
        }

@app.get("/api/system/audit", dependencies=[Depends(verify_api_key)])
async def system_audit():
    """
    Fase 15: Auditoría de salud del sistema y conectividad PROFUNDA.
    """
    from src.infrastructure.database_cloud import cloud_url, engine_cloud
    from src.domain.models import UserModel, ProductModel, CollectionItemModel, OfferModel, AuthorizedDeviceModel
    import sqlalchemy
    
    db_type = "Postgres/Supabase" if "postgresql" in cloud_url else "SQLite/Local"
    
    with SessionCloud() as db:
        try:
            # 1. Connectivity Check
            db.execute(sqlalchemy.text("SELECT 1"))
            
            # 2. Schema Check
            u_count = db.query(UserModel).count()
            p_count = db.query(ProductModel).count()
            c_count = db.query(CollectionItemModel).count()
            o_count = db.query(OfferModel).count()
            ad_count = db.query(AuthorizedDeviceModel).count()
            
            # 3. Diagnostic check for David (ID 2)
            david = db.query(UserModel).filter(UserModel.id == 2).first()
            david_items = 0
            if david:
                david_items = db.query(CollectionItemModel).filter(
                    CollectionItemModel.owner_id == 2, 
                    CollectionItemModel.acquired == True
                ).count()
            
            # 4. Connection Details (Safe)
            conn_info = str(engine_cloud.url).split("@")[-1] if "@" in str(engine_cloud.url) else "local_sqlite"
            
            # 5. Schema Audit (New Security Columns)
            security_cols = []
            try:
                col_check = db.execute(sqlalchemy.text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name IN ('reset_token', 'reset_token_expiry')
                """)).fetchall()
                security_cols = [c[0] for c in col_check]
            except:
                pass

            return {
                "status": "ONLINE",
                "database_engine": db_type,
                "connection_target": conn_info,
                "counts": {
                    "users": u_count,
                    "products": p_count,
                    "collection_items": c_count,
                    "offers": o_count,
                    "authorized_devices": ad_count
                },
                "schema_audit": {
                    "reset_token_found": "reset_token" in security_cols,
                    "reset_token_expiry_found": "reset_token_expiry" in security_cols
                },
                "david_diagnostic": {
                    "exists": david is not None,
                    "id": david.id if david else None,
                    "username": david.username if david else None,
                    "role": david.role if david else None,
                    "acquired_items_reality": david_items,
                    "target_expected": 120
                },
                "environment": {
                    "SUPABASE_DATABASE_URL_SET": settings.SUPABASE_DATABASE_URL is not None and len(settings.SUPABASE_DATABASE_URL) > 10,
                    "DATABASE_URL": settings.DATABASE_URL,
                    "PYTHON_VERSION": sys.version,
                    "SMTP_CONFIG": {
                        "HOST": settings.SMTP_HOST,
                        "PORT": settings.SMTP_PORT,
                        "USER_LOADED": settings.SMTP_USER is not None,
                        "PASS_LOADED": settings.SMTP_PASS is not None and len(settings.SMTP_PASS) > 5,
                        "SENDER": settings.SMTP_FROM
                    }
                }
            }
        except Exception as e:
            logger.error(f"AUDIT FAILURE: {e}")
            return {
                "status": "ERROR",
                "database_engine": db_type,
                "error_detail": str(e),
                "hint": "Check if DB credentials are correct or if the DB server is reachable."
            }

@app.post("/api/users/{user_id}/location")
async def update_user_location(user_id: int, location: str):
    """
    Fase 15: Actualiza la ubicación geográfica del usuario para el Oráculo Logístico.
    """
    from src.domain.models import UserModel
    
    with SessionCloud() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user.location = location.upper()
        db.commit()
        return {"status": "success", "location": user.location}

# --- SHIELD ARCHITECTURE: VAULT & EXCEL BRIDGE ---

@app.get("/api/vault/generate")
async def api_generate_vault(user_id: int = 2):
    """Genera la Bóveda SQLite personal."""
    from src.application.services.vault_service import VaultService
    from fastapi.responses import FileResponse
    
    vault_service = VaultService()
    with SessionCloud() as db:
        try:
            vault_path = vault_service.generate_user_vault(user_id, db)
            return FileResponse(
                path=vault_path, 
                filename=os.path.basename(vault_path),
                media_type='application/x-sqlite3'
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vault/stage")
async def api_stage_vault(user_id: int = 2, file_path: str = None):
    """Sube una bóveda a la Zona de Cuarentena (Shield Protocol)."""
    from src.application.services.vault_service import VaultService
    from src.domain.models import StagedImportModel
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Archivo no encontrado.")
        
    vault_service = VaultService()
    try:
        vault_service.stage_vault_import(user_id, file_path)
        
        # Guardar en base de datos para aprobación de Admin
        with SessionCloud() as db:
            stage = StagedImportModel(
                user_id=user_id,
                import_type="VAULT",
                status="PENDING",
                data_payload=json.dumps({"source_file": file_path}),
                impact_summary="Importación de Bóveda SQLite detectada. Pendiente de auditoría del Arquitecto."
            )
            db.add(stage)
            db.commit()
            
        return {"status": "success", "message": "Bóveda en Cuarentena. Un administrador debe validar la inyección."}
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Shield Protocol Bloqueó Infección: {str(e)}")

@app.post("/api/excel/sync")
async def api_sync_excel(user_id: int = 2):
    """Sincroniza el Excel local de David (Excel Bridge) con los datos del Oráculo."""
    from src.application.services.excel_manager import ExcelManager
    from pathlib import Path
    
    # Ruta relativa al proyecto (funciona en Windows local Y dentro de Docker)
    project_root = Path(__file__).resolve().parents[3]  # src/interfaces/api/main.py -> 3 niveles hasta raíz
    DAVID_EXCEL = str(project_root / "data" / "MOTU" / "lista_MOTU.xlsx")
    
    manager = ExcelManager(DAVID_EXCEL)
    success = manager.sync_acquisitions_from_db(user_id)
    
    if success:
        return {"status": "success", "message": "Excel Bridge sincronizado con éxito."}
    else:
        raise HTTPException(status_code=500, detail="Fallo en la sincronización del Excel. Verifique la ruta y el formato.")


if __name__ == "__main__":
    import uvicorn
    try:
        from scripts.ox3_shield import apply_3ox_shield
        apply_3ox_shield()
    except Exception:
        pass
        
    # Escuchar en 0.0.0.0 para facilitar conectividad en Docker/Red Local
    uvicorn.run("src.interfaces.api.main:app", host="0.0.0.0", port=8000, reload=True)

# --- Logistics & Cart (Phase 1) ---

@app.post("/api/logistics/calculate-cart")
async def api_calculate_cart(request: CartRequest):
    """
    Simulador de Factura (Fictional Cart).
    Agrupa ítems por tienda y aplica reglas de envío/impuestos.
    """
    try:
        user_location = "ES"
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.id == request.user_id).first()
            if user:
                user_location = user.location

        items_dict = [item.model_dump() for item in request.items]
        result = LogisticsService.calculate_cart(items_dict, user_location)
        return result
    except Exception as e:
        logger.error(f"Error calculating cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- DISPOSITIVOS Y SEGURIDAD (OJO DE SAURON) ---

@app.get("/api/admin/devices", dependencies=[Depends(verify_api_key)])
async def get_all_devices():
    """Lista todos los dispositivos que han intentado conectar."""
    with SessionCloud() as db:
        devices = db.query(AuthorizedDeviceModel).order_by(desc(AuthorizedDeviceModel.created_at)).all()
        return devices

@app.post("/api/admin/devices/{device_id}/authorize", dependencies=[Depends(verify_api_key)])
async def authorize_device(device_id: str):
    """Autoriza un dispositivo para acceso permanente."""
    with SessionCloud() as db:
        success = SecurityShield.authorize_device(device_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        # Opcional: Notificar por Telegram que ya está autorizado
        alert_msg = f"✅ *ORÁCULO INFORMA*\n\nEl dispositivo `{device_id}` ha sido **AUTORIZADO** con éxito."
        import asyncio
        asyncio.create_task(SecurityShield.send_telegram_alert(alert_msg))
        
        return {"status": "success", "message": f"Dispositivo {device_id} autorizado."}

@app.delete("/api/admin/devices/{device_id}", dependencies=[Depends(verify_api_key)])
async def revoke_device(device_id: str):
    """Revoca el acceso de un dispositivo."""
    with SessionCloud() as db:
        device = db.query(AuthorizedDeviceModel).filter(AuthorizedDeviceModel.device_id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        db.delete(device)
        db.commit()
        return {"status": "success", "message": f"Acceso revocado para {device_id}."}
