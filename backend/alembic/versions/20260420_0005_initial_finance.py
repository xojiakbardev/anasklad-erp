"""initial finance schema

Revision ID: 20260420_0005
Revises: 20260420_0004
Create Date: 2026-04-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260420_0005"
down_revision: Union[str, None] = "20260420_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True)),
        sa.Column("external_id", sa.BigInteger, nullable=False),
        sa.Column("external_order_id", sa.BigInteger),
        sa.Column("external_shop_id", sa.BigInteger),
        sa.Column("external_product_id", sa.BigInteger),
        sa.Column("status", sa.String(32)),
        sa.Column("sold_at", sa.DateTime(timezone=True)),
        sa.Column("product_title", sa.String(512)),
        sa.Column("sku_title", sa.String(512)),
        sa.Column("amount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("amount_returns", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cancelled", sa.Integer, nullable=False, server_default="0"),
        sa.Column("seller_price", sa.BigInteger),
        sa.Column("purchase_price", sa.BigInteger),
        sa.Column("commission", sa.BigInteger),
        sa.Column("logistic_delivery_fee", sa.BigInteger),
        sa.Column("seller_profit", sa.BigInteger),
        sa.Column("withdrawn_profit", sa.BigInteger),
        sa.Column("return_cause", sa.String(256)),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_sales_source_external"),
        schema="finance",
    )
    for col in ["tenant_id", "integration_id", "shop_id", "external_order_id", "external_product_id", "status", "sold_at"]:
        op.create_index(f"ix_finance_sales_{col}", "sales", [col], schema="finance")

    op.create_table(
        "expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True)),
        sa.Column("external_id", sa.BigInteger, nullable=False),
        sa.Column("external_shop_id", sa.BigInteger),
        sa.Column("name", sa.String(256)),
        sa.Column("source_kind", sa.String(64)),
        sa.Column("type", sa.String(16)),
        sa.Column("status", sa.String(16)),
        sa.Column("payment_price", sa.BigInteger),
        sa.Column("amount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("date_created", sa.DateTime(timezone=True)),
        sa.Column("date_service", sa.DateTime(timezone=True)),
        sa.Column("code", sa.String(64)),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_expenses_source_external"),
        schema="finance",
    )
    for col in ["tenant_id", "integration_id", "shop_id", "source_kind", "type", "date_service"]:
        op.create_index(f"ix_finance_expenses_{col}", "expenses", [col], schema="finance")


def downgrade() -> None:
    op.drop_table("expenses", schema="finance")
    op.drop_table("sales", schema="finance")
