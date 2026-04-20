"""SQLAlchemy ORM for the auth schema."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from anasklad.core.db.base import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(128))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TenantModel(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "auth"}

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth"}

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, index=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
