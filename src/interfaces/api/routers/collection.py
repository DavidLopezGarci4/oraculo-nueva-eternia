import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy import select

from src.domain.models import CollectionItemModel, OfferModel, ProductModel, UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import get_current_user, scope_user_id as _scope_user_id

def trigger_excel_sync_background(user_id: int, product_id: int):
    try:
        from src.domain.models import UserModel, ProductModel
        from src.application.services.excel_manager import ExcelManager
        from src.infrastructure.database_cloud import SessionCloud
        from pathlib import Path
        
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
            if not user or not product:
                return
            
            is_admin = user.role == 'admin' or user.username == 'David'
            username = user.username
            is_vintage = product.is_vintage or False
            
        project_root = Path(__file__).resolve().parents[4]
        
        if is_admin:
            if is_vintage:
                excel_path = project_root / "data" / "MOTU" / "lista_vintage.xlsx"
            else:
                excel_path = project_root / "data" / "MOTU" / "lista_MOTU.xlsx"
        else:
            excel_path = project_root / "data" / "MOTU" / f"lista_MOTU_{username}.xlsx"
            
        if excel_path.exists():
            manager = ExcelManager(str(excel_path))
            manager.sync_acquisitions_from_db(user_id)
            logger.info(f"🔄 Automatically synchronized Excel at: {excel_path}")
    except Exception as e:
        logger.error(f"❌ Failed to auto-sync Excel: {e}")
from src.interfaces.api.schemas import (
    CollectionItemUpdateRequest,
    CollectionToggleRequest,
    ProductOutput,
)

router = APIRouter(tags=["collection"])


@router.get("/api/collection", response_model=List[ProductOutput])
async def get_collection(
    user_id: int,
    is_vintage: bool = False,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    search: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
):
    user_id = _scope_user_id(current_user, user_id)
    from src.application.services.valuation_service import ValuationService

    with SessionCloud() as db:
        valuation_service = ValuationService(db)

        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user_location = user.location

        query = (
            select(ProductModel, CollectionItemModel)
            .join(CollectionItemModel, ProductModel.id == CollectionItemModel.product_id)
            .where(CollectionItemModel.owner_id == user_id)
        )
        if is_vintage:
            query = query.where(ProductModel.is_vintage == True)
        else:
            query = query.where(ProductModel.is_vintage.is_not(True))

        if search:
            search_term = f"%{search}%"
            query = query.where(
                ProductModel.name.ilike(search_term) |
                ProductModel.figure_id.ilike(search_term) |
                ProductModel.upc.ilike(search_term) |
                ProductModel.asin.ilike(search_term)
            )

        results = db.execute(query).all()

        if not results:
            return []

        output_list = []
        for product, collection_item in results:
            market_val = valuation_service.get_consolidated_value(product, user_location)

            is_grail = False
            grail_score = 0.0
            if market_val > 0 and product.retail_price and product.retail_price > 0:
                roi = ((market_val - product.retail_price) / product.retail_price) * 100
                if roi > 100:
                    is_grail = True
                    grail_score = min(roi / 10, 100)

            output_list.append(
                ProductOutput(
                    id=product.id,
                    name=product.name,
                    ean=product.ean,
                    image_url=product.image_url,
                    category=product.category,
                    sub_category=product.sub_category,
                    figure_id=product.figure_id,
                    variant_name=product.variant_name,
                    purchase_price=collection_item.purchase_price or 0.0,
                    retail_price=product.retail_price or 0.0,
                    market_value=round(market_val, 2),
                    avg_market_price=product.avg_market_price or 0.0,
                    p25_price=product.p25_price or 0.0,
                    landing_price=round(market_val, 2),
                    is_grail=is_grail,
                    grail_score=round(grail_score, 1),
                    is_wish=not collection_item.acquired,
                    acquired_at=collection_item.acquired_at.isoformat() if collection_item.acquired_at else None,
                    condition=collection_item.condition or "MOC",
                    grading=collection_item.grading or 10.0,
                    notes=collection_item.notes,
                    is_vintage=product.is_vintage or False,
                )
            )

        if offset is not None or limit is not None:
            start = offset or 0
            end = start + limit if limit is not None else len(output_list)
            return output_list[start:end]

        return output_list


@router.get("/api/guardian/export/excel")
async def export_excel(user_id: int = 1, current_user: UserModel = Depends(get_current_user)):
    user_id = _scope_user_id(current_user, user_id)
    try:
        from src.application.services.guardian_service import GuardianService

        with SessionCloud() as db:
            file_path = GuardianService.export_collection_to_excel(db, user_id)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo Excel")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        logger.error(f"Excel Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/guardian/export/excel/vintage")
async def export_excel_vintage(user_id: int = 1, current_user: UserModel = Depends(get_current_user)):
    user_id = _scope_user_id(current_user, user_id)
    try:
        from src.application.services.guardian_service import GuardianService

        with SessionCloud() as db:
            file_path = GuardianService.export_vintage_collection_to_excel(db, user_id)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar el archivo Excel Vintage")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        logger.error(f"Excel Vintage Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/guardian/export/sqlite")
async def export_sqlite(user_id: int = 1, current_user: UserModel = Depends(get_current_user)):
    user_id = _scope_user_id(current_user, user_id)
    try:
        from src.application.services.guardian_service import GuardianService

        with SessionCloud() as db:
            file_path = GuardianService.export_collection_to_sqlite(db, user_id)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error al generar la Bóveda SQLite")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/x-sqlite3",
        )
    except Exception as e:
        logger.error(f"SQLite Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/collection/toggle")
async def toggle_collection(
    request: CollectionToggleRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
):
    scoped_user_id = _scope_user_id(current_user, request.user_id)
    with SessionCloud() as db:
        item = db.query(CollectionItemModel).filter(
            CollectionItemModel.product_id == request.product_id,
            CollectionItemModel.owner_id == scoped_user_id,
        ).first()

        if item:
            if not item.acquired and not request.wish:
                item.acquired = True
                action = "upgraded"
            else:
                db.delete(item)
                action = "removed"
        else:
            new_item = CollectionItemModel(
                product_id=request.product_id,
                owner_id=scoped_user_id,
                acquired=not request.wish,
            )
            db.add(new_item)
            action = "added_wish" if request.wish else "added_owned"

        db.commit()
        background_tasks.add_task(trigger_excel_sync_background, scoped_user_id, request.product_id)
        return {"status": "success", "action": action, "product_id": request.product_id}


@router.patch("/api/collection/{product_id}")
async def update_collection_item(
    product_id: int,
    request: CollectionItemUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
):
    scoped_user_id = _scope_user_id(current_user, request.user_id)
    with SessionCloud() as db:
        item = db.query(CollectionItemModel).filter(
            CollectionItemModel.product_id == product_id,
            CollectionItemModel.owner_id == scoped_user_id,
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado en tu colección")

        if request.condition is not None:
            item.condition = request.condition
        if request.grading is not None:
            item.grading = request.grading
        if request.purchase_price is not None:
            item.purchase_price = request.purchase_price
        if request.notes is not None:
            item.notes = request.notes
        if request.acquired is not None:
            item.acquired = request.acquired
        if request.acquired_at is not None:
            try:
                clean_date = request.acquired_at.replace("Z", "")
                item.acquired_at = datetime.fromisoformat(clean_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido")

        db.commit()
        background_tasks.add_task(trigger_excel_sync_background, scoped_user_id, product_id)
        return {"status": "success", "message": "Detalles del legado actualizados"}
