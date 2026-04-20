"""SQLAlchemy ORM for the catalog schema."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
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


class ProductModel(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "source", "external_id", name="uq_products_tenant_source_external"
        ),
        {"schema": "catalog"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    integration_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    shop_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)

    external_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    category: Mapped[str | None] = mapped_column(String(256))
    image_url: Mapped[str | None] = mapped_column(String(1024))
    rating: Mapped[str | None] = mapped_column(String(16))
    commission_percent: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class VariantModel(Base):
    __tablename__ = "variants"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "source", "external_id", name="uq_variants_tenant_source_external"
        ),
        {"schema": "catalog"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("catalog.products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    external_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(64), index=True)
    article: Mapped[str | None] = mapped_column(String(128))
    seller_item_code: Mapped[str | None] = mapped_column(String(128))
    ikpu: Mapped[str | None] = mapped_column(String(64))
    characteristics: Mapped[str | None] = mapped_column(Text)

    price: Mapped[int | None] = mapped_column(BigInteger)
    purchase_price: Mapped[int | None] = mapped_column(BigInteger)
    commission_percent: Mapped[float | None] = mapped_column(Float)

    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    qty_fbo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qty_fbs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qty_sold_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qty_returned_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    returned_percentage: Mapped[float | None] = mapped_column(Float)

    preview_image_url: Mapped[str | None] = mapped_column(String(1024))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
