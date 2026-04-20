"""initial integrations schema

Revision ID: 20260420_0002
Revises: 20260420_0001
Create Date: 2026-04-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260420_0002"
down_revision: Union[str, None] = "20260420_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("credentials_encrypted", sa.Text, nullable=False),
        sa.Column("rate_per_second", sa.Float, nullable=False, server_default="5.0"),
        sa.Column("rate_burst", sa.Integer, nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_checked_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text),
        sa.UniqueConstraint("tenant_id", "source", "label", name="uq_integration_tenant_source_label"),
        schema="integrations",
    )
    op.create_index(
        "ix_integrations_integrations_tenant_id",
        "integrations",
        ["tenant_id"],
        schema="integrations",
    )

    op.create_table(
        "shops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.BigInteger, nullable=False),
        sa.Column("name", sa.String(256), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("integration_id", "external_id", name="uq_shop_integration_external"),
        schema="integrations",
    )
    op.create_index(
        "ix_integrations_shops_integration_id",
        "shops",
        ["integration_id"],
        schema="integrations",
    )
    op.create_index(
        "ix_integrations_shops_tenant_id",
        "shops",
        ["tenant_id"],
        schema="integrations",
    )


def downgrade() -> None:
    op.drop_index("ix_integrations_shops_tenant_id", table_name="shops", schema="integrations")
    op.drop_index("ix_integrations_shops_integration_id", table_name="shops", schema="integrations")
    op.drop_table("shops", schema="integrations")
    op.drop_index(
        "ix_integrations_integrations_tenant_id", table_name="integrations", schema="integrations"
    )
    op.drop_table("integrations", schema="integrations")
