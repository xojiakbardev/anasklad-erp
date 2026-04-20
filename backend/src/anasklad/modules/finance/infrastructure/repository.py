"""Finance repositories: Sales + Expenses."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.finance.infrastructure.models import ExpenseModel, SaleModel


class SaleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, fields: dict) -> None:
        fields = dict(fields)
        fields.setdefault("id", uuid.uuid4())
        fields.setdefault("source", "uzum")
        stmt = pg_insert(SaleModel).values(**fields)
        update_set = {
            k: stmt.excluded[k]
            for k in fields
            if k not in ("id", "tenant_id", "source", "integration_id")
        }
        stmt = stmt.on_conflict_do_update(
            constraint="uq_sales_source_external", set_=update_set
        )
        await self._session.execute(stmt)

    async def list(
        self,
        *,
        tenant_id: uuid.UUID,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 0,
        size: int = 100,
    ) -> tuple[list[SaleModel], int]:
        conditions = [SaleModel.tenant_id == tenant_id]
        if date_from:
            conditions.append(SaleModel.sold_at >= date_from)
        if date_to:
            conditions.append(SaleModel.sold_at < date_to)

        count_stmt = select(func.count()).select_from(SaleModel).where(and_(*conditions))
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(SaleModel)
            .where(and_(*conditions))
            .order_by(SaleModel.sold_at.desc().nulls_last())
            .limit(size)
            .offset(page * size)
        )
        rows = list((await self._session.execute(stmt)).scalars().all())
        return rows, int(total)

    async def summary(
        self,
        *,
        tenant_id: uuid.UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> dict:
        stmt = select(
            func.coalesce(func.sum(SaleModel.seller_price), 0).label("revenue"),
            func.coalesce(func.sum(SaleModel.commission), 0).label("commission"),
            func.coalesce(func.sum(SaleModel.logistic_delivery_fee), 0).label("logistics"),
            func.coalesce(func.sum(SaleModel.purchase_price), 0).label("purchase_cost"),
            func.coalesce(func.sum(SaleModel.seller_profit), 0).label("profit"),
            func.coalesce(func.sum(SaleModel.withdrawn_profit), 0).label("withdrawn"),
            func.count(SaleModel.id).label("sales_count"),
            func.coalesce(func.sum(SaleModel.amount), 0).label("units_sold"),
            func.coalesce(func.sum(SaleModel.amount_returns), 0).label("units_returned"),
        ).where(
            and_(
                SaleModel.tenant_id == tenant_id,
                SaleModel.sold_at >= date_from,
                SaleModel.sold_at < date_to,
            )
        )
        row = (await self._session.execute(stmt)).one()
        return {
            "revenue": int(row.revenue or 0),
            "commission": int(row.commission or 0),
            "logistics": int(row.logistics or 0),
            "purchase_cost": int(row.purchase_cost or 0),
            "profit": int(row.profit or 0),
            "withdrawn": int(row.withdrawn or 0),
            "sales_count": int(row.sales_count or 0),
            "units_sold": int(row.units_sold or 0),
            "units_returned": int(row.units_returned or 0),
        }

    async def daily_profit(
        self,
        *,
        tenant_id: uuid.UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> list[tuple[datetime, int, int]]:
        """Group by day: (day, revenue, profit)."""
        day = func.date_trunc("day", SaleModel.sold_at).label("day")
        stmt = (
            select(
                day,
                func.coalesce(func.sum(SaleModel.seller_price), 0).label("revenue"),
                func.coalesce(func.sum(SaleModel.seller_profit), 0).label("profit"),
            )
            .where(
                and_(
                    SaleModel.tenant_id == tenant_id,
                    SaleModel.sold_at >= date_from,
                    SaleModel.sold_at < date_to,
                )
            )
            .group_by(day)
            .order_by(day)
        )
        rows = (await self._session.execute(stmt)).all()
        return [(r.day, int(r.revenue or 0), int(r.profit or 0)) for r in rows]

    async def top_products(
        self,
        *,
        tenant_id: uuid.UUID,
        date_from: datetime,
        date_to: datetime,
        limit: int = 10,
    ) -> list[dict]:
        stmt = (
            select(
                SaleModel.external_product_id,
                SaleModel.product_title,
                func.coalesce(func.sum(SaleModel.amount), 0).label("units"),
                func.coalesce(func.sum(SaleModel.seller_price), 0).label("revenue"),
                func.coalesce(func.sum(SaleModel.seller_profit), 0).label("profit"),
            )
            .where(
                and_(
                    SaleModel.tenant_id == tenant_id,
                    SaleModel.sold_at >= date_from,
                    SaleModel.sold_at < date_to,
                )
            )
            .group_by(SaleModel.external_product_id, SaleModel.product_title)
            .order_by(func.sum(SaleModel.seller_profit).desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            {
                "product_id": r.external_product_id,
                "title": r.product_title or "—",
                "units": int(r.units or 0),
                "revenue": int(r.revenue or 0),
                "profit": int(r.profit or 0),
            }
            for r in rows
        ]


class ExpenseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, fields: dict) -> None:
        fields = dict(fields)
        fields.setdefault("id", uuid.uuid4())
        fields.setdefault("source", "uzum")
        stmt = pg_insert(ExpenseModel).values(**fields)
        update_set = {
            k: stmt.excluded[k]
            for k in fields
            if k not in ("id", "tenant_id", "source", "integration_id")
        }
        stmt = stmt.on_conflict_do_update(
            constraint="uq_expenses_source_external", set_=update_set
        )
        await self._session.execute(stmt)

    async def list(
        self,
        *,
        tenant_id: uuid.UUID,
        page: int = 0,
        size: int = 100,
    ) -> tuple[list[ExpenseModel], int]:
        count_stmt = (
            select(func.count())
            .select_from(ExpenseModel)
            .where(ExpenseModel.tenant_id == tenant_id)
        )
        total = (await self._session.execute(count_stmt)).scalar_one()
        stmt = (
            select(ExpenseModel)
            .where(ExpenseModel.tenant_id == tenant_id)
            .order_by(ExpenseModel.date_service.desc().nulls_last())
            .limit(size)
            .offset(page * size)
        )
        rows = list((await self._session.execute(stmt)).scalars().all())
        return rows, int(total)
