"""Catalog API schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ProductRowResponse(_Base):
    product_id: UUID
    external_id: int
    title: str
    category: str | None
    image_url: str | None
    sku_count: int
    qty_fbo_total: int
    qty_fbs_total: int
    min_price: int | None
    max_price: int | None
    updated_at: datetime


class ProductListResponse(_Base):
    items: list[ProductRowResponse]
    total: int
    page: int
    size: int


class VariantResponse(_Base):
    id: UUID
    external_id: int
    title: str
    barcode: str | None
    article: str | None
    ikpu: str | None
    characteristics: str | None
    price: int | None
    purchase_price: int | None
    qty_fbo: int
    qty_fbs: int
    qty_sold_total: int
    qty_returned_total: int
    returned_percentage: float | None
    archived: bool
    blocked: bool
    preview_image_url: str | None


class SyncResultResponse(_Base):
    integration_id: UUID
    products_upserted: int = Field(ge=0)
    variants_upserted: int = Field(ge=0)
    shops_synced: int = Field(ge=0)
