"""SQLAlchemy ORM for finance schema."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from anasklad.core.db.base import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class SaleModel(Base):
    """One row per sold item from /v1/finance/orders (flat view)."""

    __tablename__ = "sales"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_sales_source_external"),
        {"schema": "finance"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    integration_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    shop_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)

    external_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # SellerOrderItem.id
    external_order_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    external_shop_id: Mapped[int | None] = mapped_column(BigInteger)
    external_product_id: Mapped[int | None] = mapped_column(BigInteger, index=True)

    status: Mapped[str | None] = mapped_column(String(32), index=True)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    product_title: Mapped[str | None] = mapped_column(String(512))
    sku_title: Mapped[str | None] = mapped_column(String(512))

    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    amount_returns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cancelled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    seller_price: Mapped[int | None] = mapped_column(BigInteger)
    purchase_price: Mapped[int | None] = mapped_column(BigInteger)
    commission: Mapped[int | None] = mapped_column(BigInteger)
    logistic_delivery_fee: Mapped[int | None] = mapped_column(BigInteger)
    seller_profit: Mapped[int | None] = mapped_column(BigInteger)
    withdrawn_profit: Mapped[int | None] = mapped_column(BigInteger)

    return_cause: Mapped[str | None] = mapped_column(String(256))

    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ExpenseModel(Base):
    """One row per /v1/finance/expenses payment."""

    __tablename__ = "expenses"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_expenses_source_external"),
        {"schema": "finance"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    integration_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    shop_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)

    external_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    external_shop_id: Mapped[int | None] = mapped_column(BigInteger)

    name: Mapped[str | None] = mapped_column(String(256))
    source_kind: Mapped[str | None] = mapped_column(String(64), index=True)
    type: Mapped[str | None] = mapped_column(String(16), index=True)  # INCOME/OUTCOME
    status: Mapped[str | None] = mapped_column(String(16))
    payment_price: Mapped[int | None] = mapped_column(BigInteger)
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    date_created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_service: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    code: Mapped[str | None] = mapped_column(String(64))

    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
