from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product title or brand name")
    description: Optional[str] = Field(None, description="Detailed product description")
    source_url: Optional[str] = Field(None, max_length=2048, description="URL to landing page or product listing")
    category: Optional[str] = Field(None, max_length=100, description="Product domain or market category")
    target_market: Optional[str] = Field(None, max_length=100, description="Target customer segment")
    status: str = Field("DRAFT", description="Lifecycle status: DRAFT, ACTIVE, ARCHIVED")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    source_url: Optional[str] = Field(None, max_length=2048)
    category: Optional[str] = Field(None, max_length=100)
    target_market: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
