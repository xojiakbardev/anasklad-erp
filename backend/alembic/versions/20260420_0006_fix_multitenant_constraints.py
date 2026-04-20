"""Fix multi-tenant integrity: tenant-scoped unique constraints + intra-schema FKs

Revision ID: 20260420_0006
Revises: 20260420_0005
Create Date: 2026-04-20

Changes:
1. Drop `(source, external_id)` unique constraints; replace with
   `(tenant_id, source, external_id)` across catalog / orders / finance.
2. Add ON DELETE CASCADE FKs within the same schema:
   - catalog.variants.product_id → catalog.products.id
   - orders.fbs_order_items.order_id → orders.fbs_orders.id
   - integrations.shops.integration_id → integrations.integrations.id
3. Reorder integrations.delete_cascade — no DB-level cross-schema FK
   (by design), so cross-schema cleanup is handled in the service layer.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "20260420_0006"
down_revision: Union[str, None] = "20260420_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------- catalog.products ----------
    op.drop_constraint(
        "uq_products_source_external", "products", schema="catalog", type_="unique"
    )
    op.create_unique_constraint(
        "uq_products_tenant_source_external",
        "products",
        ["tenant_id", "source", "external_id"],
        schema="catalog",
    )

    # ---------- catalog.variants ----------
    op.drop_constraint(
        "uq_variants_source_external", "variants", schema="catalog", type_="unique"
    )
    op.create_unique_constraint(
        "uq_variants_tenant_source_external",
        "variants",
        ["tenant_id", "source", "external_id"],
        schema="catalog",
    )
    op.create_foreign_key(
        "fk_variants_product_id_products",
        "variants",
        "products",
        ["product_id"],
        ["id"],
        source_schema="catalog",
        referent_schema="catalog",
        ondelete="CASCADE",
    )

    # ---------- orders.fbs_orders ----------
    op.drop_constraint(
        "uq_fbs_orders_source_external",
        "fbs_orders",
        schema="orders",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_fbs_orders_tenant_source_external",
        "fbs_orders",
        ["tenant_id", "source", "external_id"],
        schema="orders",
    )

    # ---------- orders.fbs_order_items ----------
    op.create_foreign_key(
        "fk_fbs_items_order_id_fbs_orders",
        "fbs_order_items",
        "fbs_orders",
        ["order_id"],
        ["id"],
        source_schema="orders",
        referent_schema="orders",
        ondelete="CASCADE",
    )

    # ---------- finance.sales ----------
    op.drop_constraint(
        "uq_sales_source_external", "sales", schema="finance", type_="unique"
    )
    op.create_unique_constraint(
        "uq_sales_tenant_source_external",
        "sales",
        ["tenant_id", "source", "external_id"],
        schema="finance",
    )

    # ---------- finance.expenses ----------
    op.drop_constraint(
        "uq_expenses_source_external", "expenses", schema="finance", type_="unique"
    )
    op.create_unique_constraint(
        "uq_expenses_tenant_source_external",
        "expenses",
        ["tenant_id", "source", "external_id"],
        schema="finance",
    )

    # ---------- integrations.shops ----------
    # Shops belong to an integration — cascade-delete makes the service-layer
    # cleanup simpler (only one explicit delete per foreign schema).
    op.create_foreign_key(
        "fk_shops_integration_id_integrations",
        "shops",
        "integrations",
        ["integration_id"],
        ["id"],
        source_schema="integrations",
        referent_schema="integrations",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # ---------- integrations.shops ----------
    op.drop_constraint(
        "fk_shops_integration_id_integrations",
        "shops",
        schema="integrations",
        type_="foreignkey",
    )

    # ---------- finance.expenses ----------
    op.drop_constraint(
        "uq_expenses_tenant_source_external",
        "expenses",
        schema="finance",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_expenses_source_external",
        "expenses",
        ["source", "external_id"],
        schema="finance",
    )

    # ---------- finance.sales ----------
    op.drop_constraint(
        "uq_sales_tenant_source_external", "sales", schema="finance", type_="unique"
    )
    op.create_unique_constraint(
        "uq_sales_source_external", "sales", ["source", "external_id"], schema="finance"
    )

    # ---------- orders.fbs_order_items ----------
    op.drop_constraint(
        "fk_fbs_items_order_id_fbs_orders",
        "fbs_order_items",
        schema="orders",
        type_="foreignkey",
    )

    # ---------- orders.fbs_orders ----------
    op.drop_constraint(
        "uq_fbs_orders_tenant_source_external",
        "fbs_orders",
        schema="orders",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_fbs_orders_source_external",
        "fbs_orders",
        ["source", "external_id"],
        schema="orders",
    )

    # ---------- catalog.variants ----------
    op.drop_constraint(
        "fk_variants_product_id_products",
        "variants",
        schema="catalog",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_variants_tenant_source_external",
        "variants",
        schema="catalog",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_variants_source_external",
        "variants",
        ["source", "external_id"],
        schema="catalog",
    )

    # ---------- catalog.products ----------
    op.drop_constraint(
        "uq_products_tenant_source_external",
        "products",
        schema="catalog",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_products_source_external",
        "products",
        ["source", "external_id"],
        schema="catalog",
    )
