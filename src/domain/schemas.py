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

class ProductCreate(ProductBase):
    pass

class ProductSchema(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class CollectionItemBase(BaseModel):
    product_id: int
    owner_id: int
    quantity: int = 1
    acquisition_date: Optional[datetime] = None
    acquisition_price: Optional[float] = None
    condition: Optional[str] = "Loose"
    notes: Optional[str] = None

class CollectionItemCreate(CollectionItemBase):
    pass

class CollectionItemSchema(CollectionItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
