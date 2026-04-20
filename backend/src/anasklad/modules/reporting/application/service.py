"""Reporting queries — ABC, turnover, low-stock.

Reads from catalog.variants + finance.sales directly.
No writes. Implemented as a service to keep a clean facade for the api router.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.catalog.infrastructure.models import ProductModel, VariantModel
from anasklad.modules.finance.infrastructure.models import SaleModel


@dataclass(slots=True, frozen=True)
class AbcRow:
    product_id: uuid.UUID
    external_id: int
    title: str
    units_sold: int
    revenue: int
    profit: int
    share: float
    cumulative_share: float
    rank: str  # A, B, C, N


@dataclass(slots=True, frozen=True)
class TurnoverRow:
    variant_id: uuid.UUID
    product_title: str
    sku_title: str
    qty_fbo: int
    qty_fbs: int
    avg_daily_sales: float
    days_of_stock: float | None  # None when avg_daily_sales==0


@dataclass(slots=True, frozen=True)
class StockRow:
    variant_id: uuid.UUID
    product_id: uuid.UUID
    product_title: str
    sku_title: str
    barcode: str | None
    qty_fbo: int
    qty_fbs: int
    qty_total: int
    price: int | None
    purchase_price: int | None
    archived: bool
    blocked: bool


class ReportingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ---------- ABC ----------

    async def abc(
        self, *, tenant_id: uuid.UUID, days: int = 30
    ) -> list[AbcRow]:
        date_from = datetime.now(UTC) - timedelta(days=days)
        stmt = (
            select(
                SaleModel.external_product_id.label("ext_id"),
                SaleModel.product_title.label("title"),
                func.coalesce(func.sum(SaleModel.amount), 0).label("units"),
                func.coalesce(func.sum(SaleModel.seller_price), 0).label("revenue"),
                func.coalesce(func.sum(SaleModel.seller_profit), 0).label("profit"),
            )
            .where(
                and_(
                    SaleModel.tenant_id == tenant_id,
                    SaleModel.sold_at >= date_from,
                )
            )
            .group_by(SaleModel.external_product_id, SaleModel.product_title)
            .order_by(desc("revenue"))
        )
        rows = (await self._session.execute(stmt)).all()
        if not rows:
            return []

        total_revenue = sum(int(r.revenue or 0) for r in rows)
        if total_revenue <= 0:
            return []

        # Map external product_id → internal UUID (1 query)
        ext_ids = [r.ext_id for r in rows if r.ext_id is not None]
        id_map: dict[int, uuid.UUID] = {}
        if ext_ids:
            id_stmt = select(ProductModel.external_id, ProductModel.id).where(
                and_(
                    ProductModel.tenant_id == tenant_id,
                    ProductModel.external_id.in_(ext_ids),
                )
            )
            id_map = {eid: pid for eid, pid in (await self._session.execute(id_stmt)).all()}

        result: list[AbcRow] = []
        cumulative = 0
        for r in rows:
            revenue = int(r.revenue or 0)
            cumulative += revenue
            share = revenue / total_revenue
            cum_share = cumulative / total_revenue
            if cum_share <= 0.80:
                rank = "A"
            elif cum_share <= 0.95:
                rank = "B"
            elif cum_share <= 1.0 and revenue > 0:
                rank = "C"
            else:
                rank = "N"
            result.append(
                AbcRow(
                    product_id=id_map.get(r.ext_id) or uuid.UUID(int=0),
                    external_id=int(r.ext_id) if r.ext_id else 0,
                    title=r.title or "—",
                    units_sold=int(r.units or 0),
                    revenue=revenue,
                    profit=int(r.profit or 0),
                    share=share,
                    cumulative_share=cum_share,
                    rank=rank,
                )
            )
        return result

    # ---------- Turnover ----------

    async def turnover(
        self, *, tenant_id: uuid.UUID, days: int = 30, limit: int = 200
    ) -> list[TurnoverRow]:
        date_from = datetime.now(UTC) - timedelta(days=days)
        sales_sub = (
            select(
                SaleModel.external_product_id.label("ext_pid"),
                func.coalesce(func.sum(SaleModel.amount), 0).label("total_units"),
            )
            .where(
                and_(
                    SaleModel.tenant_id == tenant_id,
                    SaleModel.sold_at >= date_from,
                )
            )
            .group_by(SaleModel.external_product_id)
            .subquery()
        )

        stmt = (
            select(
                VariantModel.id.label("variant_id"),
                ProductModel.title.label("product_title"),
                VariantModel.title.label("sku_title"),
                ProductModel.external_id.label("product_ext_id"),
                VariantModel.qty_fbo,
                VariantModel.qty_fbs,
                func.coalesce(sales_sub.c.total_units, 0).label("sold"),
            )
            .join(ProductModel, ProductModel.id == VariantModel.product_id)
            .outerjoin(
                sales_sub, sales_sub.c.ext_pid == ProductModel.external_id
            )
            .where(
                and_(
                    VariantModel.tenant_id == tenant_id,
                    VariantModel.archived.is_(False),
                )
            )
            .order_by(desc("sold"))
            .limit(limit)
        )

        rows = (await self._session.execute(stmt)).all()
        result: list[TurnoverRow] = []
        for r in rows:
            total_qty = int(r.qty_fbo or 0) + int(r.qty_fbs or 0)
            avg_daily = (int(r.sold or 0)) / days
            days_of_stock = total_qty / avg_daily if avg_daily > 0 else None
            result.append(
                TurnoverRow(
                    variant_id=r.variant_id,
                    product_title=r.product_title or "—",
                    sku_title=r.sku_title or "—",
                    qty_fbo=int(r.qty_fbo or 0),
                    qty_fbs=int(r.qty_fbs or 0),
                    avg_daily_sales=round(avg_daily, 2),
                    days_of_stock=round(days_of_stock, 1) if days_of_stock is not None else None,
                )
            )
        return result

    # ---------- Low-stock ----------

    async def low_stock(
        self,
        *,
        tenant_id: uuid.UUID,
        fbs_threshold: int = 5,
        fbo_threshold: int = 5,
        limit: int = 500,
    ) -> list[StockRow]:
        stmt = (
            select(
                VariantModel.id.label("variant_id"),
                VariantModel.product_id,
                ProductModel.title.label("product_title"),
                VariantModel.title.label("sku_title"),
                VariantModel.barcode,
                VariantModel.qty_fbo,
                VariantModel.qty_fbs,
                VariantModel.price,
                VariantModel.purchase_price,
                VariantModel.archived,
                VariantModel.blocked,
            )
            .join(ProductModel, ProductModel.id == VariantModel.product_id)
            .where(
                and_(
                    VariantModel.tenant_id == tenant_id,
                    VariantModel.archived.is_(False),
                    (VariantModel.qty_fbs <= fbs_threshold)
                    | (VariantModel.qty_fbo <= fbo_threshold),
                )
            )
            .order_by(
                case(
                    (VariantModel.qty_fbo + VariantModel.qty_fbs == 0, 0),
                    else_=1,
                ),
                VariantModel.qty_fbo + VariantModel.qty_fbs,
            )
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            StockRow(
                variant_id=r.variant_id,
                product_id=r.product_id,
                product_title=r.product_title or "—",
                sku_title=r.sku_title or "—",
                barcode=r.barcode,
                qty_fbo=int(r.qty_fbo or 0),
                qty_fbs=int(r.qty_fbs or 0),
                qty_total=int(r.qty_fbo or 0) + int(r.qty_fbs or 0),
                price=int(r.price) if r.price else None,
                purchase_price=int(r.purchase_price) if r.purchase_price else None,
                archived=bool(r.archived),
                blocked=bool(r.blocked),
            )
            for r in rows
        ]

    # ---------- Stock list (full) ----------

    async def stocks(
        self,
        *,
        tenant_id: uuid.UUID,
        search: str | None = None,
        only_available: bool = False,
        only_low: bool = False,
        only_out: bool = False,
        page: int = 0,
        size: int = 100,
    ) -> tuple[list[StockRow], int]:
        conditions = [
            VariantModel.tenant_id == tenant_id,
            VariantModel.archived.is_(False),
        ]
        total_expr = VariantModel.qty_fbo + VariantModel.qty_fbs
        if only_available:
            conditions.append(total_expr > 0)
        if only_low:
            conditions.append(total_expr > 0)
            conditions.append(total_expr <= 10)
        if only_out:
            conditions.append(total_expr == 0)
        if search:
            conditions.append(
                (VariantModel.title.ilike(f"%{search}%"))
                | (ProductModel.title.ilike(f"%{search}%"))
                | (VariantModel.barcode.ilike(f"%{search}%"))
            )

        base = (
            select(
                VariantModel.id.label("variant_id"),
                VariantModel.product_id,
                ProductModel.title.label("product_title"),
                VariantModel.title.label("sku_title"),
                VariantModel.barcode,
                VariantModel.qty_fbo,
                VariantModel.qty_fbs,
                VariantModel.price,
                VariantModel.purchase_price,
                VariantModel.archived,
                VariantModel.blocked,
            )
            .join(ProductModel, ProductModel.id == VariantModel.product_id)
            .where(and_(*conditions))
        )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        rows = (
            await self._session.execute(
                base.order_by(total_expr.desc()).limit(size).offset(page * size)
            )
        ).all()

        items = [
            StockRow(
                variant_id=r.variant_id,
                product_id=r.product_id,
                product_title=r.product_title or "—",
                sku_title=r.sku_title or "—",
                barcode=r.barcode,
                qty_fbo=int(r.qty_fbo or 0),
                qty_fbs=int(r.qty_fbs or 0),
                qty_total=int(r.qty_fbo or 0) + int(r.qty_fbs or 0),
                price=int(r.price) if r.price else None,
                purchase_price=int(r.purchase_price) if r.purchase_price else None,
                archived=bool(r.archived),
                blocked=bool(r.blocked),
            )
            for r in rows
        ]
        return items, int(total)
