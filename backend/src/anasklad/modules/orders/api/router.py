"""Orders HTTP endpoints."""
from __future__ import annotations

import uuid
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query, Response

from anasklad.core.http.deps import current_user
from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import TokenPayload
from anasklad.modules.orders.api.schemas import (
    CancelRequest,
    OrderDetailResponse,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
    SyncOrdersResponse,
)
from anasklad.modules.orders.application.service import OrderService
from anasklad.modules.orders.infrastructure.models import FbsOrderItemModel, FbsOrderModel

router = APIRouter(prefix="/orders", tags=["orders"], route_class=DishkaRoute)


def _tenant(p: TokenPayload) -> uuid.UUID:
    if p.tenant_id is None:
        raise AuthError("token missing tenant claim")
    return uuid.UUID(p.tenant_id)


def _order_to_response(o: FbsOrderModel) -> OrderResponse:
    return OrderResponse(
        id=o.id,
        external_id=o.external_id,
        invoice_number=o.invoice_number,
        status=o.status,
        scheme=o.scheme,
        price=o.price,
        cancel_reason=o.cancel_reason,
        date_created=o.date_created,
        accept_until=o.accept_until,
        deliver_until=o.deliver_until,
        completed_date=o.completed_date,
        updated_at=o.updated_at,
    )


def _item_to_response(i: FbsOrderItemModel) -> OrderItemResponse:
    return OrderItemResponse(
        id=i.id,
        external_sku_id=i.external_sku_id,
        sku_title=i.sku_title,
        product_title=i.product_title,
        amount=i.amount,
        seller_price=i.seller_price,
        purchase_price=i.purchase_price,
        commission=i.commission,
        logistic_delivery_fee=i.logistic_delivery_fee,
        seller_profit=i.seller_profit,
    )


@router.get("", response_model=OrderListResponse)
async def list_orders(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[OrderService],
    status: str | None = Query(default=None, max_length=48),
    shop_id: uuid.UUID | None = None,
    page: int = Query(default=0, ge=0),
    size: int = Query(default=100, ge=1, le=500),
) -> OrderListResponse:
    tenant_id = _tenant(payload)
    rows, total = await service.list(
        tenant_id=tenant_id, status=status, shop_id=shop_id, page=page, size=size
    )
    counts = await service.counts(tenant_id=tenant_id)
    return OrderListResponse(
        items=[_order_to_response(r) for r in rows],
        total=total,
        page=page,
        size=size,
        counts_by_status=counts,
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[OrderService],
) -> OrderDetailResponse:
    tenant_id = _tenant(payload)
    order, items = await service.get(tenant_id=tenant_id, order_id=order_id)
    return OrderDetailResponse(
        **_order_to_response(order).model_dump(),
        items=[_item_to_response(i) for i in items],
    )


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm(
    order_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[OrderService],
) -> OrderResponse:
    tenant_id = _tenant(payload)
    updated = await service.confirm(tenant_id=tenant_id, order_id=order_id)
    return _order_to_response(updated)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel(
    order_id: uuid.UUID,
    body: CancelRequest,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[OrderService],
) -> OrderResponse:
    tenant_id = _tenant(payload)
    updated = await service.cancel(
        tenant_id=tenant_id, order_id=order_id, reason=body.reason, comment=body.comment
    )
    return _order_to_response(updated)


@router.get("/{order_id}/label")
async def label_pdf(
    order_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[OrderService],
    size: str = Query(default="LARGE", pattern="^(LARGE|BIG)$"),
) -> Response:
    tenant_id = _tenant(payload)
    pdf = await service.label_pdf(tenant_id=tenant_id, order_id=order_id, size=size)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="label-{order_id}.pdf"'},
    )


@router.post("/integrations/{integration_id}/sync", response_model=SyncOrdersResponse)
async def sync_orders(
    integration_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[OrderService],
) -> SyncOrdersResponse:
    tenant_id = _tenant(payload)
    result = await service.sync(tenant_id=tenant_id, integration_id=integration_id)
    return SyncOrdersResponse(
        orders_upserted=result.orders_upserted, shops_synced=result.shops_synced
    )
