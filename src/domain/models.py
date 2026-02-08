from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import List, Optional

DOMAIN_VERSION = "1.2.1-GUARDIAN"

from src.domain.base import Base

# PriceAlertModel moved down for dependency resolution

class ProductModel(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True) # Removed unique=True to allow variants with same name
    ean: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, default="Masters of the Universe")
    sub_category: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True) # e.g. "Origins", "Turtles of Grayskull"
    
    # Financial & Meta Data (Phase 6 & 16)
    retail_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    
    # Phase 50: Market Intelligence & Sentiment
    popularity_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0) # Total collectors from AF411
    market_momentum: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=1.0) # Sentiment trend multiplier
    asin: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True) # Amazon ID
    upc: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True) # Universal Product Code
    
    # Phase 41e & 10 (Master Nexus): Strict Market Segregation
    avg_retail_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    p25_retail_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    
    avg_p2p_price_us: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) # From AF411 (Master Benchmark)
    avg_p2p_price_eu: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) # From Deep Scrape (Local Real-time)
    p25_p2p_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    
    market_gap: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) # Delta % between US and EU
    release_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Legacy Fallbacks (Synchronized with new fields for backward compatibility)
    avg_market_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) 
    p25_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) 
    avg_p2p_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) # Backward compat alias for EU
    
    # Phase 0: Multivariant Identity
    figure_id: Mapped[Optional[str]] = mapped_column(String, index=True, unique=True, nullable=True)
    variant_name: Mapped[Optional[str]] = mapped_column(String, nullable=True) # e.g. "V2", "Repaint"
    image_hash: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True) # Perceptual Hash for visual dedupe
    master_image_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True) # ActionFigure411 reference hash
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offers: Mapped[List["OfferModel"]] = relationship(
        "OfferModel", 
        back_populates="product", 
        cascade="all, delete-orphan"
    )
    
    collection_items: Mapped[List["CollectionItemModel"]] = relationship(
        "CollectionItemModel",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    aliases: Mapped[List["ProductAliasModel"]] = relationship(
        "ProductAliasModel",
        back_populates="product",
        cascade="all, delete-orphan"
    )

class OfferModel(Base):
    __tablename__ = "offers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    
    shop_name: Mapped[str] = mapped_column(String, index=True)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="EUR")
    url: Mapped[str] = mapped_column(String, index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 3OX Audit Trail
    receipt_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)

    # Analytics
    min_price: Mapped[float] = mapped_column(Float, default=0.0)
    max_price: Mapped[float] = mapped_column(Float, default=0.0)
    source_type: Mapped[str] = mapped_column(String, default="Retail") # Retail, Peer-to-Peer
    
    # Validation flags
    validation_status: Mapped[str] = mapped_column(String, default="VALIDATED")
    anomaly_flags: Mapped[Optional[str]] = mapped_column(String, nullable=True) 
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)
    
    # Phase 39: Auction Intelligence
    sale_type: Mapped[str] = mapped_column(String, default="Retail") # Retail, Auction, Fixed_P2P
    expiry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bids_count: Mapped[int] = mapped_column(Integer, default=0)
    time_left_raw: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Phase 41: Market Intelligence
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    original_listing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_price_update: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="offers")
    price_history: Mapped[List["PriceHistoryModel"]] = relationship(
        "PriceHistoryModel", 
        back_populates="offer",
        cascade="all, delete-orphan"
    )

class CollectionItemModel(Base):
    __tablename__ = "collection_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), unique=False, index=True) # Allow multiple users to own same product
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True) # Link to User
    
    acquired: Mapped[bool] = mapped_column(Boolean, default=False)
    condition: Mapped[str] = mapped_column(String, default="New")
    grading: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=10.0) # Condition Grade (1-10)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0) # Financial Investment
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    acquired_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="collection_items")
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="collection_items")

# Update ProductModel to include relationship
ProductModel.collection_item = relationship(
    "CollectionItemModel", 
    uselist=False, 
    back_populates="product",
    cascade="all, delete-orphan",
    overlaps="collection_items"
)

class PendingMatchModel(Base):
    """
    Stores scraped items that weren't confidently matched to a Product.
    These sit in 'Purgatory' until the user assigns them.
    """
    __tablename__ = "pending_matches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Scraped Data
    scraped_name: Mapped[str] = mapped_column(String)
    ean: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="EUR")
    url: Mapped[str] = mapped_column(String, unique=True) # Avoid dupe pending items
    shop_name: Mapped[str] = mapped_column(String)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_type: Mapped[str] = mapped_column(String, default="Retail") # Retail, Peer-to-Peer
    
    # 3OX Audit Trail
    receipt_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Validation flags
    validation_status: Mapped[str] = mapped_column(String, default="PENDING") # PENDING, VALIDATED, REJECTED
    anomaly_flags: Mapped[Optional[str]] = mapped_column(String, nullable=True) # JSON string with detected anomalies
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False) # Manually blocked by admin/user
    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)

    # Phase 39: Auction Intelligence
    sale_type: Mapped[str] = mapped_column(String, default="Retail") # Retail, Auction, Fixed_P2P
    expiry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bids_count: Mapped[int] = mapped_column(Integer, default=0)
    time_left_raw: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Phase 41: Market Intelligence
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    original_listing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_price_update: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    found_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ProductAliasModel(Base):
    """
    Capa de Alias (Phase 0): Mapea URLs de scraping a un Product ID interno.
    Esto garantiza que si el nombre en la tienda cambia, el link siga apuntando al mismo producto.
    """
    __tablename__ = "product_aliases"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    
    source_url: Mapped[str] = mapped_column(String, index=True, unique=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=True) # Si fue validado por un matching de alta confianza
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="aliases")
    
    
# --- AUDIT TRAIL (BASTIÓN DE DATOS) ---
class OfferHistoryModel(Base):
    """
    Historial de movimientos de ofertas para recuperación y auditoría.
    Registra cambios de estado (NUEVO, ENLAZADO, PURGATORIO, ELIMINADO).
    """
    __tablename__ = "offer_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    offer_url: Mapped[str] = mapped_column(String, index=True)
    product_name: Mapped[str] = mapped_column(String)
    shop_name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    action_type: Mapped[str] = mapped_column(String) # NEW, LINKED, UNLINKED, PURGED
    details: Mapped[Optional[str]] = mapped_column(String, nullable=True) # JSON or descriptive text
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# PriceAlertModel promoted to top (moved here for coherence)
class PriceAlertModel(Base):
    """
    Vigilancia de precios del Centinela.
    """
    __tablename__ = "price_alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    target_price: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    product: Mapped["ProductModel"] = relationship("ProductModel")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="price_alerts")



class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=False) # Changed to False to allow admin/user same email
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="viewer") # admin, viewer
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    location: Mapped[str] = mapped_column(String, default="ES") # e.g. 'ES', 'DE', 'IT' - Phase 15 Logistics
    
    price_alerts: Mapped[List["PriceAlertModel"]] = relationship("PriceAlertModel", back_populates="user", cascade="all, delete-orphan")
    collection_items: Mapped[List["CollectionItemModel"]] = relationship(
        "CollectionItemModel",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

class ScraperStatusModel(Base):
    __tablename__ = "scraper_status"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spider_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String) # running, completed, error
    items_scraped: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[int] = mapped_column(Integer, default=0) # 0-100
    total_items_estimated: Mapped[int] = mapped_column(Integer, default=0)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlackcludedItemModel(Base):
    """Items explicitly discarded by the user to prevent re-scraping."""
    __tablename__ = "blackcluded_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String, unique=True, index=True)
    scraped_name: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String, default="Retail")
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Validation flags
    validation_status: Mapped[str] = mapped_column(String, default="VALIDATED")
    anomaly_flags: Mapped[Optional[str]] = mapped_column(String, nullable=True) # JSON containing reasons
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PriceHistoryModel(Base):
    """Tracks price changes over time for analytics."""
    __tablename__ = "price_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"))
    price: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_snapshot: Mapped[bool] = mapped_column(Boolean, default=False) # True if price didn't change but we recorded the state
    
    offer: Mapped["OfferModel"] = relationship("OfferModel", back_populates="price_history")

class ScraperExecutionLogModel(Base):
    """
    Immutable log of every scraper execution run.
    Provides forensic history and audit trail.
    """
    __tablename__ = "scraper_execution_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spider_name: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String) # success, error, interrupted
    items_found: Mapped[int] = mapped_column(Integer, default=0)
    new_items: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Context
    trigger_type: Mapped[str] = mapped_column(String, default="manual") # manual, scheduled
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logs: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Full execution logs for UI

class StagedImportModel(Base):
    """
    Zona de Cuarentena (Shield Architecture): Almacena datos importados pendientes de validación.
    """
    __tablename__ = "staged_imports"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    import_type: Mapped[str] = mapped_column(String, default="VAULT") # VAULT, EXCEL
    status: Mapped[str] = mapped_column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    
    data_payload: Mapped[str] = mapped_column(String) # JSON con los datos a importar
    impact_summary: Mapped[str] = mapped_column(String) # Resumen legible: "Adds 20 items, updates 5"
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class SyncQueueModel(Base):
    """
    Cola de Sincronización Transaccional (Fase 3).
    Almacena las acciones pendientes de subir a la nube.
    """
    __tablename__ = "sync_queue"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    action_type: Mapped[str] = mapped_column(String) # LINK, DISCARD, ADD_PRODUCT, UPDATE_PRICE
    payload: Mapped[str] = mapped_column(String) # JSON string with all metadata
    
    status: Mapped[str] = mapped_column(String, default="PENDING") # PENDING, SYNCED, FAILED
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_msg: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class LogisticRuleModel(Base):
    """
    Oráculo Logístico (Phase 15): Reglas de envío y tasas por tienda y ubicación.
    """
    __tablename__ = "logistic_rules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shop_name: Mapped[str] = mapped_column(String, index=True)
    country_code: Mapped[str] = mapped_column(String, index=True, default="ES")
    
    base_shipping: Mapped[float] = mapped_column(Float, default=0.0)
    free_shipping_threshold: Mapped[float] = mapped_column(Float, default=0.0)
    vat_multiplier: Mapped[float] = mapped_column(Float, default=1.0) # e.g. 1.21 for ES
    custom_fees: Mapped[float] = mapped_column(Float, default=0.0) # Gastos fijos aduana/gestión
    strategy_key: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Para lógica especial programática
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KaizenInsightModel(Base):
    """
    Qualitative repository for anti-bot findings, DOM changes, and improvement ideas.
    This is the primary source of 'Trial & Error' knowledge.
    """
    __tablename__ = "kaizen_insights"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spider_name: Mapped[str] = mapped_column(String, index=True)
    
    insight_type: Mapped[str] = mapped_column(String) # dom_change, anti_bot_detected, idea, improvement
    severity: Mapped[str] = mapped_column(String, default="info") # info, warning, critical
    
    content: Mapped[str] = mapped_column(String) # Detailed description
    pattern_observed: Mapped[Optional[str]] = mapped_column(String, nullable=True) # CSS selectors, timing, etc.
    proposed_solution: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="pending") # pending, implemented, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

__all__ = [
    "Base", 
    "ProductModel", 
    "OfferModel", 
    "CollectionItemModel", 
    "PendingMatchModel", 
    "PriceAlertModel", 
    "UserModel", 
    "ScraperStatusModel", 
    "BlackcludedItemModel", 
    "PriceHistoryModel", 
    "ScraperExecutionLogModel", 
    "KaizenInsightModel",
    "ProductAliasModel",
    "SyncQueueModel",
    "LogisticRuleModel",
    "DOMAIN_VERSION"
]

