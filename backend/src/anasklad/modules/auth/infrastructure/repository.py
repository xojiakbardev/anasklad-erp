"""User repository — encapsulates all ORM access for the auth module."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.auth.domain.entities import User
from anasklad.modules.auth.infrastructure.models import TenantModel, UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.lower())
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_domain(row) if row else None

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        row = await self._session.get(UserModel, user_id)
        return _to_domain(row) if row else None

    async def add(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str | None,
        tenant_id: uuid.UUID,
    ) -> User:
        model = UserModel(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            tenant_id=tenant_id,
            is_active=True,
            is_superuser=False,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_domain(model)

    async def touch_last_login(self, user_id: uuid.UUID) -> None:
        user = await self._session.get(UserModel, user_id)
        if user:
            user.last_login_at = datetime.now(UTC)

    async def create_tenant(self, name: str) -> uuid.UUID:
        t = TenantModel(name=name)
        self._session.add(t)
        await self._session.flush()
        return t.id


def _to_domain(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        password_hash=row.password_hash,
        full_name=row.full_name,
        tenant_id=row.tenant_id,
        is_active=row.is_active,
        is_superuser=row.is_superuser,
        created_at=row.created_at,
        last_login_at=row.last_login_at,
    )
