"""Order API schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class OrderItemResponse(_Base):
    id: UUID
    external_sku_id: int | None
    sku_title: str | None
    product_title: str | None
    amount: int
    seller_price: int | None
    purchase_price: int | None
    commission: int | None
    logistic_delivery_fee: int | None
    seller_profit: int | None


class OrderResponse(_Base):
    id: UUID
    external_id: int
    invoice_number: int | None
    status: str
    scheme: str | None
    price: int | None
    cancel_reason: str | None
    date_created: datetime | None
    accept_until: datetime | None
    deliver_until: datetime | None
    completed_date: datetime | None
    updated_at: datetime


class OrderDetailResponse(OrderResponse):
    items: list[OrderItemResponse]


class OrderListResponse(_Base):
    items: list[OrderResponse]
    total: int
    page: int
    size: int
    counts_by_status: dict[str, int]


class CancelRequest(_Base):
    reason: str
    comment: str | None = None


class SyncOrdersResponse(_Base):
    orders_upserted: int
    shops_synced: int
