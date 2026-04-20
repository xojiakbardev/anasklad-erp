"""initial orders schema

Revision ID: 20260420_0004
Revises: 20260420_0003
Create Date: 2026-04-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260420_0004"
down_revision: Union[str, None] = "20260420_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fbs_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.BigInteger, nullable=False),
        sa.Column("external_shop_id", sa.BigInteger, nullable=False),
        sa.Column("invoice_number", sa.BigInteger),
        sa.Column("status", sa.String(48), nullable=False),
        sa.Column("scheme", sa.String(8)),
        sa.Column("price", sa.BigInteger),
        sa.Column("cancel_reason", sa.String(64)),
        sa.Column("date_created", sa.DateTime(timezone=True)),
        sa.Column("accept_until", sa.DateTime(timezone=True)),
        sa.Column("deliver_until", sa.DateTime(timezone=True)),
        sa.Column("accepted_date", sa.DateTime(timezone=True)),
        sa.Column("delivering_date", sa.DateTime(timezone=True)),
        sa.Column("delivery_date", sa.DateTime(timezone=True)),
        sa.Column("delivered_to_dp_date", sa.DateTime(timezone=True)),
        sa.Column("completed_date", sa.DateTime(timezone=True)),
        sa.Column("date_cancelled", sa.DateTime(timezone=True)),
        sa.Column("return_date", sa.DateTime(timezone=True)),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_fbs_orders_source_external"),
        schema="orders",
    )
    op.create_index("ix_orders_fbs_orders_tenant_id", "fbs_orders", ["tenant_id"], schema="orders")
    op.create_index("ix_orders_fbs_orders_integration_id", "fbs_orders", ["integration_id"], schema="orders")
    op.create_index("ix_orders_fbs_orders_shop_id", "fbs_orders", ["shop_id"], schema="orders")
    op.create_index("ix_orders_fbs_orders_status", "fbs_orders", ["status"], schema="orders")

    op.create_table(
        "fbs_order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_sku_id", sa.BigInteger),
        sa.Column("sku_title", sa.String(512)),
        sa.Column("product_title", sa.String(512)),
        sa.Column("amount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("seller_price", sa.BigInteger),
        sa.Column("purchase_price", sa.BigInteger),
        sa.Column("commission", sa.BigInteger),
        sa.Column("logistic_delivery_fee", sa.BigInteger),
        sa.Column("seller_profit", sa.BigInteger),
        sa.Column("raw", sa.Text),
        sa.UniqueConstraint("order_id", "external_sku_id", name="uq_fbs_items_order_sku"),
        schema="orders",
    )
    op.create_index("ix_orders_fbs_order_items_tenant_id", "fbs_order_items", ["tenant_id"], schema="orders")
    op.create_index("ix_orders_fbs_order_items_order_id", "fbs_order_items", ["order_id"], schema="orders")


def downgrade() -> None:
    op.drop_index("ix_orders_fbs_order_items_order_id", table_name="fbs_order_items", schema="orders")
    op.drop_index("ix_orders_fbs_order_items_tenant_id", table_name="fbs_order_items", schema="orders")
    op.drop_table("fbs_order_items", schema="orders")
    for ix in ["status", "shop_id", "integration_id", "tenant_id"]:
        op.drop_index(f"ix_orders_fbs_orders_{ix}", table_name="fbs_orders", schema="orders")
    op.drop_table("fbs_orders", schema="orders")
