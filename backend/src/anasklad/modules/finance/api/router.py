"""Finance HTTP endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict

from anasklad.core.http.deps import current_user
from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import TokenPayload
from anasklad.modules.finance.application.service import FinanceService

router = APIRouter(prefix="/finance", tags=["finance"], route_class=DishkaRoute)


def _tenant(p: TokenPayload) -> uuid.UUID:
    if p.tenant_id is None:
        raise AuthError("token missing tenant claim")
    return uuid.UUID(p.tenant_id)


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class SaleResponse(_Base):
    id: uuid.UUID
    external_id: int
    external_order_id: int | None
    status: str | None
    sold_at: datetime | None
    product_title: str | None
    sku_title: str | None
    amount: int
    seller_price: int | None
    commission: int | None
    logistic_delivery_fee: int | None
    seller_profit: int | None
    return_cause: str | None


class SaleListResponse(_Base):
    items: list[SaleResponse]
    total: int
    page: int
    size: int


class ExpenseResponse(_Base):
    id: uuid.UUID
    external_id: int
    name: str | None
    type: str | None
    source_kind: str | None
    status: str | None
    payment_price: int | None
    amount: int
    date_service: datetime | None


class ExpenseListResponse(_Base):
    items: list[ExpenseResponse]
    total: int
    page: int
    size: int


@router.get("/summary")
async def summary(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[FinanceService],
    days: int = Query(default=30, ge=1, le=365),
) -> dict:
    tenant_id = _tenant(payload)
    return await service.summary(tenant_id=tenant_id, period_days=days)


@router.get("/sales", response_model=SaleListResponse)
async def list_sales(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[FinanceService],
    page: int = Query(default=0, ge=0),
    size: int = Query(default=100, ge=1, le=500),
) -> SaleListResponse:
    tenant_id = _tenant(payload)
    rows, total = await service.list_sales(tenant_id=tenant_id, page=page, size=size)
    return SaleListResponse(
        items=[
            SaleResponse(
                id=r.id,
                external_id=r.external_id,
                external_order_id=r.external_order_id,
                status=r.status,
                sold_at=r.sold_at,
                product_title=r.product_title,
                sku_title=r.sku_title,
                amount=r.amount,
                seller_price=r.seller_price,
                commission=r.commission,
                logistic_delivery_fee=r.logistic_delivery_fee,
                seller_profit=r.seller_profit,
                return_cause=r.return_cause,
            )
            for r in rows
        ],
        total=total,
        page=page,
        size=size,
    )


@router.get("/expenses", response_model=ExpenseListResponse)
async def list_expenses(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[FinanceService],
    page: int = Query(default=0, ge=0),
    size: int = Query(default=100, ge=1, le=500),
) -> ExpenseListResponse:
    tenant_id = _tenant(payload)
    rows, total = await service.list_expenses(tenant_id=tenant_id, page=page, size=size)
    return ExpenseListResponse(
        items=[
            ExpenseResponse(
                id=r.id,
                external_id=r.external_id,
                name=r.name,
                type=r.type,
                source_kind=r.source_kind,
                status=r.status,
                payment_price=r.payment_price,
                amount=r.amount,
                date_service=r.date_service,
            )
            for r in rows
        ],
        total=total,
        page=page,
        size=size,
    )


@router.post("/integrations/{integration_id}/sync")
async def sync_finance(
    integration_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[FinanceService],
    days: int = Query(default=30, ge=1, le=180),
) -> dict:
    tenant_id = _tenant(payload)
    result = await service.sync(
        tenant_id=tenant_id, integration_id=integration_id, days_back=days
    )
    return {"sales_upserted": result.sales_upserted, "expenses_upserted": result.expenses_upserted}
