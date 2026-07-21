from datetime import datetime
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
    condition: Optional[str] = "MOC"
    grading: Optional[float] = 10.0
    notes: Optional[str] = None
    purgatory_match_count: int = 0
    is_vintage: bool = False


class ProductEditRequest(BaseModel):
    name: str | None = None
    ean: str | None = None
    image_url: str | None = None
    category: str | None = None
    sub_category: str | None = None
    retail_price: float | None = None
    is_vintage: Optional[bool] = None


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
    acquired: Optional[bool] = None


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


class PurgatoryBulkMatchItem(BaseModel):
    pending_id: int
    product_id: int


class PurgatoryBulkMatchRequest(BaseModel):
    matches: List[PurgatoryBulkMatchItem]


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


# --- Wallapop Nexus Local Bridge (Fase 2) ---

class WallapopJobCreateRequest(BaseModel):
    query: str | None = None  # None/omitido -> "auto"


class WallapopJobResultOffer(BaseModel):
    product_name: str
    price: float
    currency: str = "EUR"
    url: str
    image_url: str | None = None
    source_type: str = "Peer-to-Peer"
    sale_type: str = "Fixed_P2P"


class WallapopJobResultsRequest(BaseModel):
    offers: List[WallapopJobResultOffer] = []
    blocked: bool = False
    error_message: str | None = None
    worker_id: str | None = None


# --- JWT ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- User Image Paths (Phase 69) ---

class UserImagePathsUpdateRequest(BaseModel):
    pc_path: Optional[str] = None
    mobile_path: Optional[str] = None


# --- Users & Dashboard Output (Fase AAA-2.2) ---
# response_model explicito para que el contrato de la API quede documentado y
# no dependa de lo que el handler decida devolver ad-hoc. Los campos y su
# nulabilidad se han verificado contra los handlers reales (users.py,
# dashboard.py) y contra UserModel/OfferModel/ProductModel en domain/models.py.

class UserSettingsOutput(BaseModel):
    id: int
    username: str
    email: str
    location: str
    role: str
    is_public_showcase: bool
    pc_image_path: Optional[str] = None
    mobile_image_path: Optional[str] = None


class UserImagePathsOutput(BaseModel):
    status: str
    pc_image_path: Optional[str] = None
    mobile_image_path: Optional[str] = None


class UserLocationOutput(BaseModel):
    status: str
    location: str


class UserPublicShowcaseOutput(BaseModel):
    status: str
    is_public_showcase: bool


class P2POpportunityOutput(BaseModel):
    id: int
    product_name: str
    ean: str | None
    image_url: str | None
    price: float
    p25_price: float
    avg_market_price: float
    saving: float
    saving_pct: float
    shop_name: str
    url: str
    opportunity_score: int | None
    landing_price: float


class FinancialHealthOutput(BaseModel):
    total_invested: float
    market_value: float
    profit_loss: float
    roi: float


class ShopDistributionOutput(BaseModel):
    shop: str | None
    count: int


class DashboardStatsOutput(BaseModel):
    total_products: int
    total_products_vintage: int
    owned_count: int
    owned_count_vintage: int
    wish_count: int
    wish_count_vintage: int
    financial: FinancialHealthOutput
    financial_vintage: FinancialHealthOutput
    match_count: int
    shop_distribution: List[ShopDistributionOutput]


class HallOfFameItemOutput(BaseModel):
    id: int
    name: str
    image_url: str | None
    figure_id: str | None
    market_value: float
    purchase_price: float
    invested_value: float
    roi: float
    roi_percentage: float


class HallOfFameGroupOutput(BaseModel):
    top_value: List[HallOfFameItemOutput]
    top_roi: List[HallOfFameItemOutput]


class HallOfFameOutput(BaseModel):
    origins: HallOfFameGroupOutput
    vintage: HallOfFameGroupOutput


class TopDealOutput(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    price: float
    landing_price: float
    shop_name: str
    url: str
    opportunity_score: int | None
    image_url: str | None


class MatchStatOutput(BaseModel):
    shop: str | None
    count: int


class MatchHistoryOutput(BaseModel):
    id: int
    product_name: str
    shop_name: str
    price: float
    action_type: str
    timestamp: str
    offer_url: str


class StatusMessageOutput(BaseModel):
    status: str
    message: str


# --- Logistics, Showcase & System Output (Fase AAA-Ola3, 3b) ---

class CartBreakdownItemOutput(BaseModel):
    name: str
    unit_price: float
    unit_price_eur: float
    quantity: int
    subtotal_eur: float


class CartShopBreakdownOutput(BaseModel):
    shop: str
    status: str
    items: List[CartBreakdownItemOutput]
    # Solo presentes cuando status == "CALCULATED" (LogisticsService.calculate_cart
    # devuelve menos campos para tiendas sin reglas configuradas, status == "PENDING_RULES").
    total_items_qty: Optional[int] = None
    fees_eur: Optional[float] = None
    shipping_eur: float
    tax_eur: float
    total_eur: float


class CartCalculationOutput(BaseModel):
    breakdown: List[CartShopBreakdownOutput]
    grand_total_eur: float
    user_location: str
    timestamp: str


class ShowcaseProductOutput(BaseModel):
    id: int
    name: str
    category: str
    sub_category: str | None
    image_url: str | None
    release_year: int | None
    figure_id: str | None
    variant_name: str | None
    is_vintage: bool | None
    avg_market_price: float | None
    p25_price: float | None


class ShowcaseItemOutput(BaseModel):
    id: int
    product_id: int
    condition: str
    grading: float | None
    notes: str | None
    # El router pasa item.acquired_at (datetime de SQLAlchemy) sin .isoformat();
    # FastAPI/Pydantic lo serializa a ISO-8601 en el JSON de salida.
    acquired_at: datetime | None
    product: ShowcaseProductOutput


class PublicShowcaseOutput(BaseModel):
    username: str
    location: str
    items: List[ShowcaseItemOutput]
    total_items: int


# --- Vault & Wallapop Jobs Output (Fase AAA-Ola3, 3b) ---
# vault.py::api_generate_vault y download_images_zip devuelven FileResponse/
# StreamingResponse (binarios) - response_model no aplica ahi, se omiten.

class WallapopJobCreatedOutput(BaseModel):
    status: str
    job_id: int
    message: str


class WallapopJobOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    status: str
    result_count: int
    error_message: str | None
    worker_id: str | None
    created_at: datetime
    claimed_at: datetime | None
    completed_at: datetime | None


class WallapopJobResultsOutput(BaseModel):
    status: str
    job_status: str
    new_items: int


# --- Auth Output (Fase AAA-Ola3, 3b) ---

class ForgotPasswordOutput(BaseModel):
    status: str
    message: str
    debug_token: str | None = None


class LoginUserOutput(BaseModel):
    id: int
    username: str
    email: str
    role: str


class LoginOutput(BaseModel):
    status: str
    user: LoginUserOutput
    access_token: str
    token_type: str
    is_sovereign: bool


class UserMinimalOutput(BaseModel):
    id: int
    username: str
    role: str


# --- Collection Output (Fase AAA-Ola3, 3b) ---
# Los 3 endpoints de exportacion (excel/excel-vintage/sqlite) devuelven
# FileResponse (binario) - response_model no aplica, se omiten a proposito.

class CollectionToggleOutput(BaseModel):
    status: str
    action: str
    product_id: int


# --- Admin Output (Fase AAA-Ola3, 3b) ---

class DuplicateProductOutput(BaseModel):
    id: int
    name: str
    image_url: str | None
    sub_category: str | None
    figure_id: str | None


class DuplicateGroupOutput(BaseModel):
    reason: str
    products: List[DuplicateProductOutput]


class AuthorizedDeviceOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    device_name: str | None
    is_authorized: bool
    last_access_at: datetime
    created_at: datetime


class TemporaryProductOutput(BaseModel):
    id: int
    name: str
    figure_id: str | None
    sub_category: str | None
    image_url: str | None
    is_vintage: bool | None
    offer_count: int
    collection_count: int


# --- Products Output (Fase AAA-Ola3, 3b) ---
# get_market_intelligence (forma anidada dinamica, con evolucion mensual y
# estrategia de puja calculadas por servicios distintos) y get_wallapop_preview
# (JSON crudo re-emitido tal cual desde la API externa de Wallapop) se dejan
# sin response_model a proposito: son datos genuinamente dinamicos/externos,
# igual que system_audit/get_sword_configs en system.py.

class ProductSearchResultOutput(BaseModel):
    id: int
    name: str
    figure_id: str | None
    sub_category: str | None
    image_url: str | None


class ProductOfferOutput(BaseModel):
    id: int
    shop_name: str
    price: float
    landing_price: float
    url: str
    last_seen: str
    min_historical: float
    opportunity_score: int
    source_type: str
    is_best: bool
    is_available: bool
    sale_type: str
    expiry_at: str | None
    bids_count: int
    time_left_raw: str | None


class MarketStatsOutput(BaseModel):
    avg: float
    min: float
    max: float
    count: int


class MarketAnalyticsOutput(BaseModel):
    retail: MarketStatsOutput
    p2p: MarketStatsOutput
    global_avg: float


class PriceHistoryPointOutput(BaseModel):
    date: str
    price: float


class ProductPriceHistoryOutput(BaseModel):
    shop_name: str
    history: List[PriceHistoryPointOutput]


class VintageProductListingOutput(BaseModel):
    id: int
    name: str
    ean: str | None
    image_url: str | None
    category: str
    sub_category: str | None
    figure_id: str | None
    release_year: int | None
    offer_id: int
    best_p2p_price: float
    best_p2p_source: str
    url: str
    condition: str
    grading: float
    bids_count: int
    time_left_raw: str | None
    sale_type: str


class VintageMiscellaneousItemOutput(BaseModel):
    id: int
    title: str
    url: str
    price: float
    currency: str
    shop_name: str
    image_url: str | None
    condition: str
    grading: float
    notes: str | None
    added_at: str | None
