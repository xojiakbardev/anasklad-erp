"""SQLAlchemy ORM for orders schema."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from anasklad.core.db.base import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class FbsOrderModel(Base):
    __tablename__ = "fbs_orders"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "source", "external_id", name="uq_fbs_orders_tenant_source_external"
        ),
        {"schema": "orders"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    integration_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    shop_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)

    external_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    external_shop_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    invoice_number: Mapped[int | None] = mapped_column(BigInteger)

    status: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    scheme: Mapped[str | None] = mapped_column(String(8))

    price: Mapped[int | None] = mapped_column(BigInteger)
    cancel_reason: Mapped[str | None] = mapped_column(String(64))

    date_created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accept_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deliver_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivering_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_to_dp_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_cancelled: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    return_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class FbsOrderItemModel(Base):
    __tablename__ = "fbs_order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "external_sku_id", name="uq_fbs_items_order_sku"),
        {"schema": "orders"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("orders.fbs_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    external_sku_id: Mapped[int | None] = mapped_column(BigInteger)
    sku_title: Mapped[str | None] = mapped_column(String(512))
    product_title: Mapped[str | None] = mapped_column(String(512))
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    seller_price: Mapped[int | None] = mapped_column(BigInteger)
    purchase_price: Mapped[int | None] = mapped_column(BigInteger)
    commission: Mapped[int | None] = mapped_column(BigInteger)
    logistic_delivery_fee: Mapped[int | None] = mapped_column(BigInteger)
    seller_profit: Mapped[int | None] = mapped_column(BigInteger)

    raw: Mapped[str | None] = mapped_column(Text)
