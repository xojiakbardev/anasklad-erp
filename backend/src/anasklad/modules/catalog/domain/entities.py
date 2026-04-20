"""Catalog domain entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Product:
    id: UUID
    tenant_id: UUID
    source: str
    integration_id: UUID
    shop_id: UUID
    external_id: int
    title: str
    category: str | None
    image_url: str | None
    rating: str | None
    commission_percent: float | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class Variant:
    """SKU — a purchasable variant of a Product."""

    id: UUID
    tenant_id: UUID
    product_id: UUID
    external_id: int  # skuId
    title: str
    barcode: str | None
    article: str | None
    seller_item_code: str | None
    ikpu: str | None
    characteristics: str | None
    price: int | None
    purchase_price: int | None
    commission_percent: float | None
    archived: bool
    blocked: bool
    qty_fbo: int
    qty_fbs: int
    qty_sold_total: int
    qty_returned_total: int
    returned_percentage: float | None
    preview_image_url: str | None
    updated_at: datetime


@dataclass(slots=True, frozen=True)
class ProductListRow:
    """Flat row for list APIs — join product + primary stats."""

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
