"""Reporting HTTP endpoints."""
from __future__ import annotations

import uuid
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict

from anasklad.core.http.deps import current_user
from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import TokenPayload
from anasklad.modules.reporting.application.service import ReportingService

router = APIRouter(prefix="/reports", tags=["reports"], route_class=DishkaRoute)


def _tenant(p: TokenPayload) -> uuid.UUID:
    if p.tenant_id is None:
        raise AuthError("token missing tenant claim")
    return uuid.UUID(p.tenant_id)


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class AbcRowDto(_Base):
    product_id: uuid.UUID
    external_id: int
    title: str
    units_sold: int
    revenue: int
    profit: int
    share: float
    cumulative_share: float
    rank: str


class TurnoverRowDto(_Base):
    variant_id: uuid.UUID
    product_title: str
    sku_title: str
    qty_fbo: int
    qty_fbs: int
    avg_daily_sales: float
    days_of_stock: float | None


class StockRowDto(_Base):
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


class StockListResponse(_Base):
    items: list[StockRowDto]
    total: int
    page: int
    size: int


@router.get("/abc", response_model=list[AbcRowDto])
async def abc_report(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[ReportingService],
    days: int = Query(default=30, ge=1, le=365),
) -> list[AbcRowDto]:
    tenant_id = _tenant(payload)
    rows = await service.abc(tenant_id=tenant_id, days=days)
    return [AbcRowDto(**row.__dict__) for row in rows]


@router.get("/turnover", response_model=list[TurnoverRowDto])
async def turnover_report(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[ReportingService],
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=200, ge=10, le=1000),
) -> list[TurnoverRowDto]:
    tenant_id = _tenant(payload)
    rows = await service.turnover(tenant_id=tenant_id, days=days, limit=limit)
    return [TurnoverRowDto(**row.__dict__) for row in rows]


@router.get("/low-stock", response_model=list[StockRowDto])
async def low_stock_report(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[ReportingService],
    fbs_threshold: int = Query(default=5, ge=0, le=100),
    fbo_threshold: int = Query(default=5, ge=0, le=100),
) -> list[StockRowDto]:
    tenant_id = _tenant(payload)
    rows = await service.low_stock(
        tenant_id=tenant_id,
        fbs_threshold=fbs_threshold,
        fbo_threshold=fbo_threshold,
    )
    return [StockRowDto(**row.__dict__) for row in rows]


@router.get("/stocks", response_model=StockListResponse)
async def stocks_list(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[ReportingService],
    search: str | None = Query(default=None, max_length=128),
    only_available: bool = False,
    only_low: bool = False,
    only_out: bool = False,
    page: int = Query(default=0, ge=0),
    size: int = Query(default=100, ge=1, le=500),
) -> StockListResponse:
    tenant_id = _tenant(payload)
    rows, total = await service.stocks(
        tenant_id=tenant_id,
        search=search,
        only_available=only_available,
        only_low=only_low,
        only_out=only_out,
        page=page,
        size=size,
    )
    return StockListResponse(
        items=[StockRowDto(**row.__dict__) for row in rows],
        total=total,
        page=page,
        size=size,
    )
