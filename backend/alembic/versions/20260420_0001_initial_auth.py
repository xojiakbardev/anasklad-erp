"""initial auth schema

Revision ID: 20260420_0001
Revises:
Create Date: 2026-04-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260420_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ("auth",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="auth",
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(128)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        schema="auth",
    )
    op.create_index("ix_auth_users_tenant_id", "users", ["tenant_id"], schema="auth")
    op.create_index("ix_auth_users_email", "users", ["email"], schema="auth")

    op.create_table(
        "refresh_tokens",
        sa.Column("jti", sa.String(64), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.false()),
        schema="auth",
    )
    op.create_index("ix_auth_refresh_tokens_user_id", "refresh_tokens", ["user_id"], schema="auth")


def downgrade() -> None:
    op.drop_index("ix_auth_refresh_tokens_user_id", table_name="refresh_tokens", schema="auth")
    op.drop_table("refresh_tokens", schema="auth")
    op.drop_index("ix_auth_users_email", table_name="users", schema="auth")
    op.drop_index("ix_auth_users_tenant_id", table_name="users", schema="auth")
    op.drop_table("users", schema="auth")
    op.drop_table("tenants", schema="auth")
