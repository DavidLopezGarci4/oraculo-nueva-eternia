from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.domain.models import UserModel
from src.interfaces.api.deps import get_current_user
from src.application.services.lore_harvester_service import LoreHarvesterService

router = APIRouter(prefix="/api/lore", tags=["Lore & Characters"])

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
    fuerza: int
    magia: int
    defensa: int
    agilidad: int
    source_url: Optional[str] = None
    is_verified: bool


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

class HarvestRequest(BaseModel):
    character_name: str

@router.get("", response_model=CharacterLoreListResponse)
def list_lore(
    search: Optional[str] = Query(None, description="Búsqueda por nombre o texto"),
    faction: Optional[str] = Query(None, description="Filtro por facción"),
    pending_only: bool = Query(False, description="Solo pendientes de revisión"),
    skip: int = Query(0, ge=0),
    limit: int = Query(150, ge=1, le=300),
    db: Session = Depends(get_db)
):
    """Lista todos los perfiles de personajes canónicos con filtros."""
    items, total = LoreHarvesterService.list_characters(
        db=db, search=search, faction=faction, pending_only=pending_only, skip=skip, limit=limit
    )
    # Contar pendientes globales
    from src.domain.models import CharacterLoreModel
    pending_count = db.query(CharacterLoreModel).filter(CharacterLoreModel.is_verified == False).count()
    return CharacterLoreListResponse(items=items, total=total, pending_count=pending_count)

@router.get("/{slug}", response_model=CharacterLoreOutput)
def get_character_lore(slug: str, db: Session = Depends(get_db)):
    """Obtiene el detalle de un personaje por su slug."""
    from src.domain.models import CharacterLoreModel
    char = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
    if not char:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return char

@router.put("/{slug}", response_model=CharacterLoreOutput)
def update_character_lore(
    slug: str,
    payload: CharacterLoreUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Actualiza y verifica el lore de un personaje."""
    updated = LoreHarvesterService.update_character(
        db=db, slug=slug, data=payload.dict(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return updated

@router.post("/harvest", response_model=CharacterLoreOutput)
def harvest_lore(
    payload: HarvestRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Fuerza la recolección de lore para un personaje desde Wiki Grayskull."""
    char = LoreHarvesterService.get_or_create_character_lore(db=db, character_name=payload.character_name)
    return char

@router.post("/harvest-product/{product_id}", response_model=CharacterLoreOutput)
def harvest_product_lore(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Fuerza la recolección determinista de lore para una figura específica desde Wiki Fandom."""
    char = LoreHarvesterService.harvest_for_product(db=db, product_id=product_id)
    if not char:
        raise HTTPException(status_code=404, detail="Figura o personaje no encontrado")
    return char

@router.post("/seed", response_model=dict)
def seed_lore(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Ejecuta el sembrado inicial del catálogo para cubrir los 507 muñecos."""
    result = LoreHarvesterService.seed_initial_catalog(db=db)
    return {"status": "ok", "result": result}
