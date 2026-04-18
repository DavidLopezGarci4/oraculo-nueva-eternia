from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# --- Cart (Fase 1) ---

class CartItem(BaseModel):
    product_name: str
    shop_name: str
    price: float
    quantity: int = 1


class CartRequest(BaseModel):
    items: List[CartItem]
    user_id: Optional[int] = 2


# --- Auth ---

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"


class UserRoleUpdateRequest(BaseModel):
    role: str


class HeroOutput(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    collection_size: int
    location: str


# --- Sync ---

class SyncAction(BaseModel):
    action_type: str
    payload: dict


# --- Product ---

class ProductOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ean: str | None
    image_url: str | None
    category: str
    sub_category: Optional[str]
    figure_id: Optional[str]
    variant_name: Optional[str]

    # Phase 41e Financials
    retail_price: float = 0.0
    avg_retail_price: float = 0.0
    p25_retail_price: float = 0.0
    avg_p2p_price: float = 0.0
    p25_p2p_price: float = 0.0

    # Financial & Intelligence (Computed/Legacy)
    purchase_price: float = 0.0
    market_value: float = 0.0
    avg_market_price: float = 0.0  # Phase 16
    p25_price: float = 0.0         # Phase 16
    landing_price: float = 0.0     # Phase 15 Logistics
    is_grail: bool = False
    grail_score: float = 0.0

    # Best Offer Tracking (Phase 44 Upgrade)
    best_p2p_price: float = 0.0
    best_p2p_source: Optional[str] = None
    is_wish: bool = False
    opportunity_score: int = 0
    acquired_at: Optional[str] = None
    condition: Optional[str] = "New"
    grading: Optional[float] = 10.0
    notes: Optional[str] = None


class ProductEditRequest(BaseModel):
    name: str | None = None
    ean: str | None = None
    image_url: str | None = None
    category: str | None = None
    sub_category: str | None = None
    retail_price: float | None = None


class ProductMergeRequest(BaseModel):
    source_id: int
    target_id: int  # "manual" or "scheduled"


# --- Collection ---

class CollectionToggleRequest(BaseModel):
    product_id: int
    user_id: int
    wish: bool = False


class CollectionItemUpdateRequest(BaseModel):
    user_id: int
    condition: Optional[str] = None
    grading: Optional[float] = None
    purchase_price: Optional[float] = None
    notes: Optional[str] = None
    acquired_at: Optional[str] = None  # ISO format


# --- Purgatory ---

class PurgatoryMatchRequest(BaseModel):
    pending_id: int
    product_id: int


class PurgatoryDiscardRequest(BaseModel):
    pending_id: int
    reason: str = "manual_discard"


class PurgatoryBulkDiscardRequest(BaseModel):
    pending_ids: List[int]
    reason: str = "manual_bulk_discard"


class AnomalyValidationRequest(BaseModel):
    id: int
    action: str  # "validate" or "block"


class RelinkOfferRequest(BaseModel):
    target_product_id: int


# --- Scrapers ---

class ScraperRunRequest(BaseModel):
    spider_name: str = "all"  # "all" or individual spider name
    trigger_type: str = "manual"
    query: str | None = None


# --- Wallapop Import (Chrome Extension) ---

class WallapopProduct(BaseModel):
    title: str
    price: float
    url: str
    imageUrl: str | None = None


class WallapopImportRequest(BaseModel):
    products: List[WallapopProduct]
