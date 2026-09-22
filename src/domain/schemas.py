from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

class ProductBase(BaseModel):
    name: str
    ean: Optional[str] = None
    image_url: Optional[str] = None
    category: str = "Masters of the Universe"
    sub_category: Optional[str] = None
    figure_id: Optional[str] = None
    variant_name: Optional[str] = None
    image_hash: Optional[str] = None
    
    # Financial & Intelligence
    retail_price: Optional[float] = 0.0
    avg_market_price: Optional[float] = 0.0
    popularity_score: Optional[int] = 0
    market_momentum: Optional[float] = 1.0
    asin: Optional[str] = None
    upc: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductSchema(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Backward compatibility alias
Product = ProductSchema

class CollectionItemBase(BaseModel):
    product_id: int
    owner_id: int
    acquired: bool = False
    condition: Optional[str] = "MOC"
    grading: Optional[float] = 10.0
    purchase_price: Optional[float] = 0.0
    notes: Optional[str] = None
    acquired_at: Optional[datetime] = None

class CollectionItemCreate(CollectionItemBase):
    pass

class CollectionItemSchema(CollectionItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    
    # Financial Intelligence Fields (Computed at runtime)
    is_grail: Optional[bool] = False
    grail_score: Optional[float] = 0.0
    current_value: Optional[float] = 0.0 # Snapshot of market value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
