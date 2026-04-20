"""initial catalog schema

Revision ID: 20260420_0003
Revises: 20260420_0002
Create Date: 2026-04-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260420_0003"
down_revision: Union[str, None] = "20260420_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.BigInteger, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("category", sa.String(256)),
        sa.Column("image_url", sa.String(1024)),
        sa.Column("rating", sa.String(16)),
        sa.Column("commission_percent", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_products_source_external"),
        schema="catalog",
    )
    op.create_index("ix_catalog_products_tenant_id", "products", ["tenant_id"], schema="catalog")
    op.create_index("ix_catalog_products_integration_id", "products", ["integration_id"], schema="catalog")
    op.create_index("ix_catalog_products_shop_id", "products", ["shop_id"], schema="catalog")

    op.create_table(
        "variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.BigInteger, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("barcode", sa.String(64)),
        sa.Column("article", sa.String(128)),
        sa.Column("seller_item_code", sa.String(128)),
        sa.Column("ikpu", sa.String(64)),
        sa.Column("characteristics", sa.Text),
        sa.Column("price", sa.BigInteger),
        sa.Column("purchase_price", sa.BigInteger),
        sa.Column("commission_percent", sa.Float),
        sa.Column("archived", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("blocked", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("qty_fbo", sa.Integer, nullable=False, server_default="0"),
        sa.Column("qty_fbs", sa.Integer, nullable=False, server_default="0"),
        sa.Column("qty_sold_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("qty_returned_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("returned_percentage", sa.Float),
        sa.Column("preview_image_url", sa.String(1024)),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_variants_source_external"),
        schema="catalog",
    )
    op.create_index("ix_catalog_variants_tenant_id", "variants", ["tenant_id"], schema="catalog")
    op.create_index("ix_catalog_variants_product_id", "variants", ["product_id"], schema="catalog")
    op.create_index("ix_catalog_variants_barcode", "variants", ["barcode"], schema="catalog")


def downgrade() -> None:
    op.drop_index("ix_catalog_variants_barcode", table_name="variants", schema="catalog")
    op.drop_index("ix_catalog_variants_product_id", table_name="variants", schema="catalog")
    op.drop_index("ix_catalog_variants_tenant_id", table_name="variants", schema="catalog")
    op.drop_table("variants", schema="catalog")
    op.drop_index("ix_catalog_products_shop_id", table_name="products", schema="catalog")
    op.drop_index("ix_catalog_products_integration_id", table_name="products", schema="catalog")
    op.drop_index("ix_catalog_products_tenant_id", table_name="products", schema="catalog")
    op.drop_table("products", schema="catalog")
