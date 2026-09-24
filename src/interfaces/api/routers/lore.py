from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from loguru import logger

from src.infrastructure.database_cloud import SessionCloud
from src.infrastructure.database import SessionLocal
from src.domain.models import UserModel, ProductModel, ProductLoreModel, CharacterLoreModel
from src.interfaces.api.deps import get_current_user
from src.application.services.lore_harvester_service import LoreHarvesterService
from src.application.services.product_lore_seed import ProductLoreSeedService

router = APIRouter(prefix="/api/lore", tags=["Lore & Characters"])

def get_lore_db():
    """Dependency para inyectar la sesión de BD (Cloud Supabase por defecto, fallback local)."""
    db = SessionCloud()
    try:
        yield db
    finally:
        db.close()

# ─── SCHEMAS LORE PERSONAJES ARQUETÍPICOS ───

class CharacterLoreOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    canonical_name: str
    subtitle: Optional[str] = None
    faction: str
    theme_key: str
    type_line: str
    special_move: str
    quote: Optional[str] = None
    flavor_quote_author: Optional[str] = None
    lore: str
    text_color: Optional[str] = "#FFFFFF"
    card_version: Optional[str] = "showcase"
    mana_cost: Optional[str] = "{2}{W}{W}"
    fuerza: int = 85
    magia: int = 75
    defensa: int = 85
    agilidad: int = 85
    source_url: Optional[str] = None
    is_verified: bool = False


class CharacterLoreListResponse(BaseModel):
    items: List[CharacterLoreOutput]
    total: int
    pending_count: int


class CharacterLoreUpdateRequest(BaseModel):
    canonical_name: Optional[str] = None
    subtitle: Optional[str] = None
    faction: Optional[str] = None
    theme_key: Optional[str] = None
    type_line: Optional[str] = None
    special_move: Optional[str] = None
    quote: Optional[str] = None
    flavor_quote_author: Optional[str] = None
    lore: Optional[str] = None
    text_color: Optional[str] = None
    card_version: Optional[str] = None
    mana_cost: Optional[str] = None
    fuerza: Optional[int] = None
    magia: Optional[int] = None
    defensa: Optional[int] = None
    agilidad: Optional[int] = None


# ─── SCHEMAS PRODUCT LORE (GRIMORIO POR ÍTEM ORIGINS) ───

class ProductLoreOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    canonical_name: str
    subtitle: Optional[str] = None
    faction: str
    theme_key: str
    type_line: str
    special_move: str
    quote: Optional[str] = None
    flavor_quote_author: Optional[str] = None
    lore: str
    source_url: Optional[str] = None
    text_color: Optional[str] = "#FFFFFF"
    card_version: Optional[str] = "showcase"
    mana_cost: Optional[str] = "{2}{W}{W}"
    fuerza: int = 85
    magia: int = 75
    defensa: int = 85
    agilidad: int = 85
    is_customized: bool = False


class ProductLoreUpdateRequest(BaseModel):
    canonical_name: Optional[str] = None
    subtitle: Optional[str] = None
    faction: Optional[str] = None
    theme_key: Optional[str] = None
    type_line: Optional[str] = None
    special_move: Optional[str] = None
    quote: Optional[str] = None
    flavor_quote_author: Optional[str] = None
    lore: Optional[str] = None
    source_url: Optional[str] = None
    text_color: Optional[str] = None
    card_version: Optional[str] = None
    mana_cost: Optional[str] = None
    fuerza: Optional[int] = None
    magia: Optional[int] = None
    defensa: Optional[int] = None
    agilidad: Optional[int] = None


class ProductLoreListItem(BaseModel):
    product_id: int
    product_name: str
    sub_category: Optional[str] = None
    image_url: Optional[str] = None
    canonical_name: str
    subtitle: Optional[str] = None
    faction: str
    special_move: str
    quote: Optional[str] = None
    flavor_quote_author: Optional[str] = None
    lore: str
    is_customized: bool = False


class ProductLoreListResponse(BaseModel):
    items: List[ProductLoreListItem]
    total: int


class HarvestRequest(BaseModel):
    character_name: str


# ─── ENDPOINTS LORE POR ÍTEM (EXCLUSIVO ORIGINS) ───

@router.get("/product/{product_id}", response_model=ProductLoreOutput)
def get_product_lore(product_id: int, db: Session = Depends(get_lore_db)):
    """
    Obtiene el lore y reverso de blíster de una figura específica de la línea Origins.
    Excluye estrictamente productos vintage (is_vintage == True).
    Si aún no existe registro, genera automáticamente el perfil canónico para que nunca esté vacío.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Figura no encontrada")

    if product.is_vintage:
        raise HTTPException(
            status_code=400,
            detail="El Grimorio Lore solo aplica a la línea Masters of the Universe Origins (excluye Vintage)."
        )

    # Buscar en tabla product_lore
    lore_entry = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == product_id).first()
    if lore_entry:
        return lore_entry

    # Fallback automático: Generar y persistir el perfil determinista para este producto
    try:
        data = ProductLoreSeedService.generate_default_lore_for_product(product, db)
        new_lore = ProductLoreModel(**data)
        db.add(new_lore)
        db.commit()
        db.refresh(new_lore)
        return new_lore
    except Exception as e:
        logger.error(f"Error generando lore fallback para producto {product_id}: {e}")
        db.rollback()
        # Fallback en memoria si ocurre un error transitorio de base de datos
        data = ProductLoreSeedService.generate_default_lore_for_product(product, db)
        return ProductLoreOutput(**data)


@router.put("/product/{product_id}", response_model=ProductLoreOutput)
def update_product_lore(
    product_id: int,
    payload: ProductLoreUpdateRequest,
    db: Session = Depends(get_lore_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Actualiza y persiste el lore de una figura Origins directamente en base de datos.
    Marca el registro como personalizado por el usuario (is_customized = True).
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Figura no encontrada")

    if product.is_vintage:
        raise HTTPException(
            status_code=400,
            detail="El Grimorio Lore solo aplica a figuras de la línea Origins."
        )

    lore_entry = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == product_id).first()

    update_dict = payload.model_dump(exclude_unset=True)
    update_dict["is_customized"] = True

    if not lore_entry:
        default_data = ProductLoreSeedService.generate_default_lore_for_product(product, db)
        default_data.update(update_dict)
        lore_entry = ProductLoreModel(**default_data)
        db.add(lore_entry)
    else:
        for k, v in update_dict.items():
            if v is not None:
                setattr(lore_entry, k, v)

    db.commit()
    db.refresh(lore_entry)

    # Sincronización secundaria con SQLite local si la sesión principal es Postgres
    try:
        with SessionLocal() as local_db:
            local_entry = local_db.query(ProductLoreModel).filter(ProductLoreModel.product_id == product_id).first()
            if not local_entry:
                local_entry = ProductLoreModel(
                    product_id=lore_entry.product_id,
                    canonical_name=lore_entry.canonical_name,
                    subtitle=lore_entry.subtitle,
                    faction=lore_entry.faction,
                    theme_key=lore_entry.theme_key,
                    type_line=lore_entry.type_line,
                    special_move=lore_entry.special_move,
                    quote=lore_entry.quote,
                    flavor_quote_author=lore_entry.flavor_quote_author,
                    lore=lore_entry.lore,
                    source_url=lore_entry.source_url,
                    text_color=lore_entry.text_color,
                    card_version=lore_entry.card_version,
                    mana_cost=lore_entry.mana_cost,
                    fuerza=lore_entry.fuerza,
                    magia=lore_entry.magia,
                    defensa=lore_entry.defensa,
                    agilidad=lore_entry.agilidad,
                    is_customized=True
                )
                local_db.add(local_entry)
            else:
                for k in update_dict.keys():
                    setattr(local_entry, k, getattr(lore_entry, k))
            local_db.commit()
    except Exception as e:
        logger.warning(f"Sincronización local de lore omitida o no requerida: {e}")

    return lore_entry


@router.get("/products", response_model=ProductLoreListResponse)
def list_product_lores(
    search: Optional[str] = Query(None, description="Búsqueda por nombre de figura o texto"),
    faction: Optional[str] = Query(None, description="Filtro por facción"),
    sub_category: Optional[str] = Query(None, description="Filtro por subcategoría / wave"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_lore_db)
):
    """
    Lista figuras de la colección Origins (is_vintage == False) con su lore asociado
    para visualización y edición en el panel del Grimorio.
    """
    query = db.query(ProductModel, ProductLoreModel).outerjoin(
        ProductLoreModel, ProductModel.id == ProductLoreModel.product_id
    ).filter(
        or_(ProductModel.is_vintage == False, ProductModel.is_vintage.is_(None))
    )

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ProductModel.name.ilike(s),
                ProductLoreModel.canonical_name.ilike(s),
                ProductLoreModel.lore.ilike(s),
                ProductLoreModel.quote.ilike(s)
            )
        )

    if faction and faction != "ALL":
        query = query.filter(ProductLoreModel.faction == faction)

    if sub_category and sub_category != "ALL":
        query = query.filter(ProductModel.sub_category == sub_category)

    total = query.count()
    results = query.order_by(ProductModel.name.asc()).offset(skip).limit(limit).all()

    items = []
    for prod, lore in results:
        if not lore:
            data = ProductLoreSeedService.generate_default_lore_for_product(prod, db)
            items.append(ProductLoreListItem(
                product_id=prod.id,
                product_name=prod.name,
                sub_category=prod.sub_category,
                image_url=prod.image_url,
                canonical_name=data["canonical_name"],
                subtitle=data["subtitle"],
                faction=data["faction"],
                special_move=data["special_move"],
                quote=data["quote"],
                flavor_quote_author=data["flavor_quote_author"],
                lore=data["lore"],
                is_customized=False
            ))
        else:
            items.append(ProductLoreListItem(
                product_id=prod.id,
                product_name=prod.name,
                sub_category=prod.sub_category,
                image_url=prod.image_url,
                canonical_name=lore.canonical_name,
                subtitle=lore.subtitle,
                faction=lore.faction,
                special_move=lore.special_move,
                quote=lore.quote,
                flavor_quote_author=lore.flavor_quote_author,
                lore=lore.lore,
                is_customized=lore.is_customized
            ))

    return ProductLoreListResponse(items=items, total=total)


# ─── ENDPOINTS LORE PERSONAJES ARQUETÍPICOS ───

@router.get("/characters", response_model=CharacterLoreListResponse)
def list_character_lore(
    search: Optional[str] = Query(None, description="Búsqueda por nombre o texto"),
    faction: Optional[str] = Query(None, description="Filtro por facción"),
    pending_only: bool = Query(False, description="Solo pendientes de revisión"),
    skip: int = Query(0, ge=0),
    limit: int = Query(150, ge=1, le=300),
    db: Session = Depends(get_lore_db)
):
    """Lista perfiles canónicos de personajes arquetípicos (He-Man, Skeletor...)."""
    items, total = LoreHarvesterService.list_characters(
        db=db, search=search, faction=faction, pending_only=pending_only, skip=skip, limit=limit
    )
    pending_count = db.query(CharacterLoreModel).filter(CharacterLoreModel.is_verified == False).count()
    return CharacterLoreListResponse(items=items, total=total, pending_count=pending_count)


@router.get("", response_model=CharacterLoreListResponse)
def list_lore_alias(
    search: Optional[str] = Query(None, description="Búsqueda por nombre o texto"),
    faction: Optional[str] = Query(None, description="Filtro por facción"),
    pending_only: bool = Query(False, description="Solo pendientes de revisión"),
    skip: int = Query(0, ge=0),
    limit: int = Query(150, ge=1, le=300),
    db: Session = Depends(get_lore_db)
):
    """Alias retrocompatible para /api/lore."""
    return list_character_lore(search=search, faction=faction, pending_only=pending_only, skip=skip, limit=limit, db=db)


@router.get("/{slug}", response_model=CharacterLoreOutput)
def get_character_lore(slug: str, db: Session = Depends(get_lore_db)):
    """Obtiene el detalle de un personaje arquetípico por su slug."""
    char = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
    if not char:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return char


@router.put("/{slug}", response_model=CharacterLoreOutput)
def update_character_lore(
    slug: str,
    payload: CharacterLoreUpdateRequest,
    db: Session = Depends(get_lore_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Actualiza el lore de un personaje arquetípico."""
    updated = LoreHarvesterService.update_character(
        db=db, slug=slug, data=payload.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return updated


@router.post("/harvest", response_model=CharacterLoreOutput)
def harvest_lore(
    payload: HarvestRequest,
    db: Session = Depends(get_lore_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Fuerza la recolección de lore para un personaje desde Wiki Grayskull."""
    char = LoreHarvesterService.get_or_create_character_lore(db=db, character_name=payload.character_name)
    return char


@router.post("/seed", response_model=dict)
def seed_origins_lore(
    force: bool = Query(False, description="Sobrescribir incluso los personalizados"),
    db: Session = Depends(get_lore_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Ejecuta el sembrado del Grimorio Lore para todas las figuras de MOTU Origins (is_vintage == False).
    """
    res = ProductLoreSeedService.seed_origins_products(db=db, force=force)
    return {"status": "ok", "result": res}
