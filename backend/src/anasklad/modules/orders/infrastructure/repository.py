"""FBS order repository."""
from __future__ import annotations

import uuid

from sqlalchemy import and_, delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.orders.infrastructure.models import (
    FbsOrderItemModel,
    FbsOrderModel,
)


class FbsOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_from_uzum(
        self,
        *,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        shop_id: uuid.UUID,
        fields: dict,
    ) -> uuid.UUID:
        """Upsert a single FBS order by (source, external_id). Returns id."""
        fields = dict(fields)
        fields["id"] = uuid.uuid4()
        fields["tenant_id"] = tenant_id
        fields["source"] = "uzum"
        fields["integration_id"] = integration_id
        fields["shop_id"] = shop_id

        stmt = pg_insert(FbsOrderModel).values(**fields)
        update_set = {
            k: stmt.excluded[k]
            for k in fields
            if k not in ("id", "tenant_id", "source", "integration_id", "shop_id")
        }
        update_set["integration_id"] = stmt.excluded.integration_id
        update_set["shop_id"] = stmt.excluded.shop_id
        stmt = stmt.on_conflict_do_update(
            constraint="uq_fbs_orders_source_external",
            set_=update_set,
        ).returning(FbsOrderModel.id)
        return (await self._session.execute(stmt)).scalar_one()

    async def replace_items(
        self,
        *,
        tenant_id: uuid.UUID,
        order_id: uuid.UUID,
        items: list[dict],
    ) -> None:
        await self._session.execute(
            delete(FbsOrderItemModel).where(FbsOrderItemModel.order_id == order_id)
        )
        if not items:
            return
        rows = [
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "order_id": order_id,
                **item,
            }
            for item in items
        ]
        await self._session.execute(pg_insert(FbsOrderItemModel).values(rows))

    async def list(
        self,
        *,
        tenant_id: uuid.UUID,
        status: str | None = None,
        shop_id: uuid.UUID | None = None,
        page: int = 0,
        size: int = 100,
    ) -> tuple[list[FbsOrderModel], int]:
        conditions = [FbsOrderModel.tenant_id == tenant_id]
        if status:
            conditions.append(FbsOrderModel.status == status)
        if shop_id:
            conditions.append(FbsOrderModel.shop_id == shop_id)

        count_stmt = select(func.count()).select_from(FbsOrderModel).where(and_(*conditions))
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(FbsOrderModel)
            .where(and_(*conditions))
            .order_by(FbsOrderModel.date_created.desc().nulls_last())
            .limit(size)
            .offset(page * size)
        )
        rows = list((await self._session.execute(stmt)).scalars().all())
        return rows, int(total)

    async def counts_by_status(
        self, *, tenant_id: uuid.UUID, statuses: list[str]
    ) -> dict[str, int]:
        stmt = (
            select(FbsOrderModel.status, func.count())
            .where(
                and_(
                    FbsOrderModel.tenant_id == tenant_id,
                    FbsOrderModel.status.in_(statuses),
                )
            )
            .group_by(FbsOrderModel.status)
        )
        rows = (await self._session.execute(stmt)).all()
        result = {s: 0 for s in statuses}
        for status, count in rows:
            result[status] = int(count)
        return result

    async def get(self, order_id: uuid.UUID, tenant_id: uuid.UUID) -> FbsOrderModel | None:
        stmt = select(FbsOrderModel).where(
            and_(FbsOrderModel.id == order_id, FbsOrderModel.tenant_id == tenant_id)
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def get_items(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[FbsOrderItemModel]:
        stmt = (
            select(FbsOrderItemModel)
            .where(
                and_(
                    FbsOrderItemModel.order_id == order_id,
                    FbsOrderItemModel.tenant_id == tenant_id,
                )
            )
            .order_by(FbsOrderItemModel.sku_title)
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def update_status(
        self, order_id: uuid.UUID, tenant_id: uuid.UUID, status: str
    ) -> None:
        existing = await self.get(order_id, tenant_id)
        if existing is not None:
            existing.status = status
