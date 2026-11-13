from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel, ProductModel, ProductLoreModel, CharacterLoreModel
from src.domain.motu_canon_database import VALID_FACTIONS, FACTION_TO_THEME
from src.interfaces.api.deps import verify_device, require_admin
from src.application.services.lore_harvester_service import LoreHarvesterService, VerifiedLoreConflict
from src.application.services.lore_dual_sync import LoreDualSync
from src.application.services.product_lore_seed import ProductLoreSeedService

# Todas las rutas exigen un dispositivo autorizado (Escudo 3OX). Las mutaciones globales
# exigen además JWT de administrador (`require_admin`) en cada endpoint.
router = APIRouter(
    prefix="/api/lore",
    tags=["Lore & Characters"],
    dependencies=[Depends(verify_device)],
)

# Campos opcionales que un PUT puede vaciar explícitamente enviando null.
_NULLABLE_FIELDS = {
    "subtitle", "quote", "flavor_quote_author", "source_url", "text_color", "card_version", "mana_cost",
}


def get_lore_db():
    """Dependency para inyectar la sesión de BD (Cloud Supabase por defecto, fallback local)."""
    db = SessionCloud()
    try:
        yield db
    finally:
        db.close()


# Catálogo cerrado de facciones: un valor fuera de VALID_FACTIONS responde 422 (validación estándar de Pydantic).
FactionName = Literal[VALID_FACTIONS]  # type: ignore[valid-type]


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
    canonical_name: Optional[str] = Field(default=None, max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=200)
    faction: Optional[FactionName] = None
    theme_key: Optional[str] = Field(default=None, max_length=60)
    type_line: Optional[str] = Field(default=None, max_length=200)
    special_move: Optional[str] = Field(default=None, max_length=200)
    quote: Optional[str] = Field(default=None, max_length=500)
    flavor_quote_author: Optional[str] = Field(default=None, max_length=200)
    lore: Optional[str] = Field(default=None, max_length=2000)
    text_color: Optional[str] = Field(default=None, max_length=20)
    card_version: Optional[str] = Field(default=None, max_length=40)
    mana_cost: Optional[str] = Field(default=None, max_length=40)
    fuerza: Optional[int] = Field(default=None, ge=1, le=100)
    magia: Optional[int] = Field(default=None, ge=1, le=100)
    defensa: Optional[int] = Field(default=None, ge=1, le=100)
    agilidad: Optional[int] = Field(default=None, ge=1, le=100)


# ─── SCHEMAS PRODUCT LORE (GRIMORIO POR ÍTEM ORIGINS) ───

class ProductLoreOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    figure_id: Optional[str] = None
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
    canonical_name: Optional[str] = Field(default=None, max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=200)
    faction: Optional[FactionName] = None
    theme_key: Optional[str] = Field(default=None, max_length=60)
    type_line: Optional[str] = Field(default=None, max_length=200)
    special_move: Optional[str] = Field(default=None, max_length=200)
    quote: Optional[str] = Field(default=None, max_length=500)
    flavor_quote_author: Optional[str] = Field(default=None, max_length=200)
    lore: Optional[str] = Field(default=None, max_length=2000)
    source_url: Optional[str] = Field(default=None, max_length=500)
    text_color: Optional[str] = Field(default=None, max_length=20)
    card_version: Optional[str] = Field(default=None, max_length=40)
    mana_cost: Optional[str] = Field(default=None, max_length=40)
    fuerza: Optional[int] = Field(default=None, ge=1, le=100)
    magia: Optional[int] = Field(default=None, ge=1, le=100)
    defensa: Optional[int] = Field(default=None, ge=1, le=100)
    agilidad: Optional[int] = Field(default=None, ge=1, le=100)


class ProductLoreListItem(BaseModel):
    product_id: int
    figure_id: Optional[str] = None
    product_name: str
    sub_category: Optional[str] = None
    image_url: Optional[str] = None
    canonical_name: str
    subtitle: Optional[str] = None
    faction: str
    theme_key: str = "castle_grayskull"
    type_line: str = ""
    special_move: str
    quote: Optional[str] = None
    flavor_quote_author: Optional[str] = None
    lore: str
    mana_cost: Optional[str] = "{2}{W}{W}"
    fuerza: int = 85
    magia: int = 75
    defensa: int = 85
    agilidad: int = 85
    is_customized: bool = False


class ProductLoreListResponse(BaseModel):
    items: List[ProductLoreListItem]
    total: int
    sub_categories: List[str] = []


class HarvestRequest(BaseModel):
    character_name: str = Field(..., min_length=1, max_length=120)
    force: bool = False


def _apply_updates(entry, update_dict: dict) -> None:
    """Aplica un PUT parcial: solo los campos opcionales pueden vaciarse con null."""
    if update_dict.get("faction") and "theme_key" not in update_dict:
        update_dict["theme_key"] = FACTION_TO_THEME.get(update_dict["faction"], entry.theme_key)
    for key, value in update_dict.items():
        if value is None and key not in _NULLABLE_FIELDS:
            continue
        setattr(entry, key, value)


def _product_lore_to_output(product: ProductModel, lore_entry: ProductLoreModel) -> ProductLoreOutput:
    data = {c.name: getattr(lore_entry, c.name) for c in ProductLoreModel.__table__.columns}
    data["figure_id"] = product.figure_id
    return ProductLoreOutput(**data)


def _list_item_from_data(prod: ProductModel, data: dict, is_customized: bool) -> ProductLoreListItem:
    return ProductLoreListItem(
        product_id=prod.id,
        figure_id=prod.figure_id,
        product_name=prod.name,
        sub_category=prod.sub_category,
        image_url=prod.image_url,
        canonical_name=data["canonical_name"],
        subtitle=data.get("subtitle"),
        faction=data["faction"],
        theme_key=data.get("theme_key") or "castle_grayskull",
        type_line=data.get("type_line") or "",
        special_move=data["special_move"],
        quote=data.get("quote"),
        flavor_quote_author=data.get("flavor_quote_author"),
        lore=data["lore"],
        mana_cost=data.get("mana_cost"),
        fuerza=data.get("fuerza", 85),
        magia=data.get("magia", 75),
        defensa=data.get("defensa", 85),
        agilidad=data.get("agilidad", 85),
        is_customized=is_customized,
    )


# ─── ENDPOINTS LORE POR ÍTEM (EXCLUSIVO ORIGINS) ───

@router.get("/product/{product_id}", response_model=ProductLoreOutput)
def get_product_lore(product_id: int, db: Session = Depends(get_lore_db)):
    """
    Obtiene el lore y reverso de blíster de una figura específica de la línea Origins.
    Excluye estrictamente productos vintage (is_vintage == True).

    Lectura pura (método seguro): nunca escribe en BD. Si aún no existe fila en `product_lore`
    devuelve el perfil canónico determinista calculado en memoria.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Figura no encontrada")

    if product.is_vintage:
        raise HTTPException(
            status_code=400,
            detail="El Grimorio Lore solo aplica a la línea Masters of the Universe Origins (excluye Vintage)."
        )

    lore_entry = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == product_id).first()
    if lore_entry:
        return _product_lore_to_output(product, lore_entry)

    data = ProductLoreSeedService.generate_default_lore_for_product(product, db)
    data["figure_id"] = product.figure_id
    return ProductLoreOutput(**data)


@router.put("/product/{product_id}", response_model=ProductLoreOutput)
def update_product_lore(
    product_id: int,
    payload: ProductLoreUpdateRequest,
    db: Session = Depends(get_lore_db),
    admin_user: UserModel = Depends(require_admin)
):
    """
    Actualiza y persiste el lore de una figura Origins (solo administrador).
    Marca el registro como personalizado (is_customized = True) y lo replica a SQLite local.
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

    if not lore_entry:
        lore_entry = ProductLoreModel(**ProductLoreSeedService.generate_default_lore_for_product(product, db))
        db.add(lore_entry)
    _apply_updates(lore_entry, update_dict)
    lore_entry.is_customized = True

    db.commit()
    db.refresh(lore_entry)
    LoreDualSync.replicate_product_lore(db, [product_id])
    return _product_lore_to_output(product, lore_entry)


@router.get("/products", response_model=ProductLoreListResponse)
def list_product_lores(
    search: Optional[str] = Query(None, description="Búsqueda por nombre, figure_id, #ID o texto"),
    faction: Optional[str] = Query(None, description="Filtro por facción"),
    sub_category: Optional[str] = Query(None, description="Filtro por subcategoría / wave"),
    customized: Optional[str] = Query(None, description="Filtro editorial: ALL | CUSTOMIZED | DEFAULT"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_lore_db)
):
    """
    Lista figuras de la colección Origins (is_vintage == False) con su lore asociado
    para visualización y edición en el panel del Grimorio. Solo lectura.
    """
    query = db.query(ProductModel, ProductLoreModel).outerjoin(
        ProductLoreModel, ProductModel.id == ProductLoreModel.product_id
    ).filter(
        or_(ProductModel.is_vintage == False, ProductModel.is_vintage.is_(None))
    )

    if search and search.strip():
        q = search.strip()
        s = f"%{q}%"
        conditions = [
            ProductModel.name.ilike(s),
            ProductModel.figure_id.ilike(s),
            ProductLoreModel.canonical_name.ilike(s),
            ProductLoreModel.subtitle.ilike(s),
            ProductLoreModel.lore.ilike(s),
            ProductLoreModel.quote.ilike(s),
        ]
        if q.startswith("#") and q[1:].isdigit():
            conditions.append(ProductModel.id == int(q[1:]))
        elif q.isdigit():
            conditions.append(ProductModel.id == int(q))
        query = query.filter(or_(*conditions))

    if faction and faction != "ALL":
        query = query.filter(ProductLoreModel.faction == faction)

    if sub_category and sub_category != "ALL":
        query = query.filter(ProductModel.sub_category == sub_category)

    if customized:
        cust_flag = customized.strip().upper()
        if cust_flag == "CUSTOMIZED":
            query = query.filter(ProductLoreModel.is_customized == True)  # noqa: E712
        elif cust_flag == "DEFAULT":
            query = query.filter(or_(ProductLoreModel.is_customized == False, ProductLoreModel.is_customized.is_(None)))  # noqa: E712

    total = query.count()
    results = query.order_by(ProductModel.name.asc()).offset(skip).limit(limit).all()

    sub_cat_rows = (
        db.query(ProductModel.sub_category)
        .filter(
            or_(ProductModel.is_vintage == False, ProductModel.is_vintage.is_(None)),
            ProductModel.sub_category.isnot(None),
        )
        .distinct()
        .order_by(ProductModel.sub_category.asc())
        .all()
    )
    sub_categories = [r[0] for r in sub_cat_rows if r[0]]

    items = []
    for prod, lore in results:
        if not lore:
            data = ProductLoreSeedService.generate_default_lore_for_product(prod, db)
            items.append(_list_item_from_data(prod, data, is_customized=False))
        else:
            items.append(_list_item_from_data(
                prod,
                {c.name: getattr(lore, c.name) for c in ProductLoreModel.__table__.columns},
                is_customized=lore.is_customized,
            ))

    return ProductLoreListResponse(items=items, total=total, sub_categories=sub_categories)


# ─── ENDPOINTS LORE PERSONAJES ARQUETÍPICOS ───

@router.get("/characters", response_model=CharacterLoreListResponse)
def list_character_lore(
    search: Optional[str] = Query(None, description="Búsqueda por nombre o texto"),
    faction: Optional[str] = Query(None, description="Filtro por facción"),
    pending_only: bool = Query(False, description="Solo pendientes de revisión"),
    skip: int = Query(0, ge=0),
    limit: int = Query(150, ge=1, le=500),
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
    limit: int = Query(150, ge=1, le=500),
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
    admin_user: UserModel = Depends(require_admin)
):
    """Actualiza el lore de un personaje arquetípico (solo administrador; queda curado por Master)."""
    data = payload.model_dump(exclude_unset=True)
    if data.get("faction") and "theme_key" not in data:
        data["theme_key"] = FACTION_TO_THEME[data["faction"]]
    updated = LoreHarvesterService.update_character(db=db, slug=slug, data=data)
    if not updated:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return updated


@router.post("/harvest", response_model=CharacterLoreOutput)
def harvest_lore(
    payload: HarvestRequest,
    db: Session = Depends(get_lore_db),
    admin_user: UserModel = Depends(require_admin)
):
    """
    Recolecta lore de un personaje desde Wiki Grayskull.
    Si el personaje ya está verificado y force=False responde 409 Conflict sin consultar la red.
    """
    slug = LoreHarvesterService.resolve_character_slug(payload.character_name)
    existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
    if existing and existing.is_verified and not payload.force:
        raise HTTPException(
            status_code=409,
            detail=f"El personaje '{slug}' ya está verificado. Confirma con force=true para sobrescribirlo."
        )
    return LoreHarvesterService.get_or_create_character_lore(
        db=db, character_name=payload.character_name, force=payload.force
    )


@router.post("/harvest-product/{product_id}", response_model=CharacterLoreOutput)
def harvest_product_lore(
    product_id: int,
    force: bool = Query(False, description="Sobrescribir un personaje ya verificado"),
    db: Session = Depends(get_lore_db),
    admin_user: UserModel = Depends(require_admin)
):
    """Recolección determinista de lore para una figura desde Wiki Fandom (409 si está verificado sin force)."""
    try:
        char = LoreHarvesterService.harvest_for_product(db=db, product_id=product_id, force=force)
    except VerifiedLoreConflict as conflict:
        raise HTTPException(
            status_code=409,
            detail=f"El personaje '{conflict.slug}' ya está verificado. Confirma con force=true para sobrescribirlo."
        )
    if not char:
        raise HTTPException(status_code=404, detail="Figura o personaje no encontrado")
    return char


@router.post("/harvest-missing", response_model=dict)
def harvest_missing_lore(
    db: Session = Depends(get_lore_db),
    admin_user: UserModel = Depends(require_admin)
):
    """Pre-carga todos los slugs existentes en una sola consulta y cosecha solo los ausentes (sin N+1)."""
    existing_slugs = {row[0] for row in db.query(CharacterLoreModel.slug).all()}
    origins = db.query(ProductModel.id, ProductModel.name, ProductModel.character_slug).filter(
        or_(ProductModel.is_vintage == False, ProductModel.is_vintage.is_(None))
    ).all()

    harvested_count = 0
    relink: dict = {}
    for product_id, product_name, current_slug in origins:
        slug = LoreHarvesterService.resolve_character_slug(product_name)
        if slug not in existing_slugs:
            # La cosecha libera la sesión SQL antes de cada petición HTTP y replica a SQLite local.
            char = LoreHarvesterService.get_or_create_character_lore(db=db, character_name=product_name)
            existing_slugs.add(char.slug)
            harvested_count += 1
        if current_slug != slug:
            relink[product_id] = slug

    for product_id, slug in relink.items():
        db.query(ProductModel).filter(ProductModel.id == product_id).update({"character_slug": slug})
    if relink:
        db.commit()
        LoreDualSync.replicate_character_slugs(db, list(relink))
    return {"status": "ok", "harvested": harvested_count, "total_checked": len(origins)}


@router.post("/seed", response_model=dict)
def seed_origins_lore(
    force: bool = Query(False, description="Sobrescribir incluso lo curado por un administrador"),
    db: Session = Depends(get_lore_db),
    admin_user: UserModel = Depends(require_admin)
):
    """
    Ejecuta el sembrado unificado del Grimorio Lore (personajes arquetípicos + figuras Origins).
    Con force=False respeta lo curado por Master; con force=True sobrescribe todo.
    Replica de forma unidireccional SessionCloud -> SQLite local.
    """
    res = ProductLoreSeedService.seed_all_dual(db=db, force=force)
    chars_res, prods_res = res["characters"], res["products"]
    return {
        "status": "ok",
        "result": {
            "created": prods_res.get("created", 0),
            "updated": prods_res.get("updated", 0),
            "total_origins": prods_res.get("total_origins", 0),
            "characters_seeded": chars_res.get("total_characters", 0)
        }
    }
