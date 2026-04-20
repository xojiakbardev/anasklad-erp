"""Integration + Shop repositories."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.integrations.domain.entities import (
    Integration,
    IntegrationStatus,
    MarketplaceSource,
    Shop,
)
from anasklad.modules.integrations.infrastructure.models import (
    IntegrationModel,
    ShopModel,
)


class IntegrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_tenant(self, tenant_id: uuid.UUID) -> list[Integration]:
        stmt = (
            select(IntegrationModel)
            .where(IntegrationModel.tenant_id == tenant_id)
            .order_by(IntegrationModel.created_at.desc())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(r) for r in rows]

    async def get(self, integration_id: uuid.UUID, tenant_id: uuid.UUID) -> Integration | None:
        stmt = select(IntegrationModel).where(
            and_(
                IntegrationModel.id == integration_id,
                IntegrationModel.tenant_id == tenant_id,
            )
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_domain(row) if row else None

    async def get_credential_raw(
        self, integration_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> str | None:
        stmt = select(IntegrationModel.credentials_encrypted).where(
            and_(
                IntegrationModel.id == integration_id,
                IntegrationModel.tenant_id == tenant_id,
            )
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add(
        self,
        *,
        tenant_id: uuid.UUID,
        source: MarketplaceSource,
        label: str,
        credentials_encrypted: str,
    ) -> Integration:
        model = IntegrationModel(
            tenant_id=tenant_id,
            source=source.value,
            label=label,
            status=IntegrationStatus.ACTIVE.value,
            credentials_encrypted=credentials_encrypted,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_domain(model)

    async def delete(self, integration_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
        stmt = delete(IntegrationModel).where(
            and_(
                IntegrationModel.id == integration_id,
                IntegrationModel.tenant_id == tenant_id,
            )
        )
        result = await self._session.execute(stmt)
        return (result.rowcount or 0) > 0

    async def mark_ok(self, integration_id: uuid.UUID) -> None:
        m = await self._session.get(IntegrationModel, integration_id)
        if m is not None:
            m.status = IntegrationStatus.ACTIVE.value
            m.last_checked_at = datetime.now(UTC)
            m.last_error = None

    async def mark_error(self, integration_id: uuid.UUID, error: str) -> None:
        m = await self._session.get(IntegrationModel, integration_id)
        if m is not None:
            m.status = IntegrationStatus.ERROR.value
            m.last_checked_at = datetime.now(UTC)
            m.last_error = error[:2000]


class ShopRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(
        self,
        *,
        integration_id: uuid.UUID,
        tenant_id: uuid.UUID,
        shops: list[tuple[int, str]],  # (external_id, name)
    ) -> list[Shop]:
        if not shops:
            return []
        rows = [
            {
                "id": uuid.uuid4(),
                "integration_id": integration_id,
                "tenant_id": tenant_id,
                "external_id": ext_id,
                "name": name,
            }
            for ext_id, name in shops
        ]
        stmt = pg_insert(ShopModel).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_shop_integration_external",
            set_={"name": stmt.excluded.name},
        )
        await self._session.execute(stmt)
        return await self.list_for_integration(integration_id, tenant_id)

    async def list_for_integration(
        self, integration_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[Shop]:
        stmt = (
            select(ShopModel)
            .where(
                and_(
                    ShopModel.integration_id == integration_id,
                    ShopModel.tenant_id == tenant_id,
                )
            )
            .order_by(ShopModel.name)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [_shop_to_domain(r) for r in rows]

    async def list_for_tenant(self, tenant_id: uuid.UUID) -> list[Shop]:
        stmt = (
            select(ShopModel)
            .where(ShopModel.tenant_id == tenant_id)
            .order_by(ShopModel.name)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [_shop_to_domain(r) for r in rows]


def _to_domain(row: IntegrationModel) -> Integration:
    return Integration(
        id=row.id,
        tenant_id=row.tenant_id,
        source=MarketplaceSource(row.source),
        label=row.label,
        status=IntegrationStatus(row.status),
        created_at=row.created_at,
        last_checked_at=row.last_checked_at,
        last_error=row.last_error,
    )


def _shop_to_domain(row: ShopModel) -> Shop:
    return Shop(
        id=row.id,
        integration_id=row.integration_id,
        tenant_id=row.tenant_id,
        external_id=row.external_id,
        name=row.name,
        created_at=row.created_at,
    )
