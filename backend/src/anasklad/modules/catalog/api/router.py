"""Catalog HTTP endpoints."""
from __future__ import annotations

import uuid
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query

from anasklad.core.http.deps import current_user
from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import TokenPayload
from anasklad.modules.catalog.api.schemas import (
    ProductListResponse,
    ProductRowResponse,
    SyncResultResponse,
    VariantResponse,
)
from anasklad.modules.catalog.application.list_products import (
    ProductListHandler,
    ProductListQuery,
)
from anasklad.modules.catalog.application.sync_uzum import CatalogSyncService
from anasklad.modules.catalog.infrastructure.repository import VariantRepository

router = APIRouter(prefix="/catalog", tags=["catalog"], route_class=DishkaRoute)


def _tenant(payload: TokenPayload) -> uuid.UUID:
    if payload.tenant_id is None:
        raise AuthError("token missing tenant claim")
    return uuid.UUID(payload.tenant_id)


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    payload: Annotated[TokenPayload, Depends(current_user)],
    handler: FromDishka[ProductListHandler],
    shop_id: uuid.UUID | None = None,
    search: str | None = Query(default=None, max_length=128),
    page: int = Query(default=0, ge=0, le=10_000),
    size: int = Query(default=50, ge=1, le=500),
) -> ProductListResponse:
    tenant_id = _tenant(payload)
    result = await handler(
        ProductListQuery(
            tenant_id=tenant_id, shop_id=shop_id, search=search, page=page, size=size
        )
    )
    return ProductListResponse(
        items=[
            ProductRowResponse(
                product_id=r.product_id,
                external_id=r.external_id,
                title=r.title,
                category=r.category,
                image_url=r.image_url,
                sku_count=r.sku_count,
                qty_fbo_total=r.qty_fbo_total,
                qty_fbs_total=r.qty_fbs_total,
                min_price=r.min_price,
                max_price=r.max_price,
                updated_at=r.updated_at,
            )
            for r in result.items
        ],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.get("/products/{product_id}/variants", response_model=list[VariantResponse])
async def list_variants(
    product_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    variants: FromDishka[VariantRepository],
) -> list[VariantResponse]:
    tenant_id = _tenant(payload)
    rows = await variants.list_for_product(tenant_id=tenant_id, product_id=product_id)
    return [
        VariantResponse(
            id=r.id,
            external_id=r.external_id,
            title=r.title,
            barcode=r.barcode,
            article=r.article,
            ikpu=r.ikpu,
            characteristics=r.characteristics,
            price=r.price,
            purchase_price=r.purchase_price,
            qty_fbo=r.qty_fbo,
            qty_fbs=r.qty_fbs,
            qty_sold_total=r.qty_sold_total,
            qty_returned_total=r.qty_returned_total,
            returned_percentage=r.returned_percentage,
            archived=r.archived,
            blocked=r.blocked,
            preview_image_url=r.preview_image_url,
        )
        for r in rows
    ]


@router.post("/integrations/{integration_id}/sync", response_model=SyncResultResponse)
async def sync_integration(
    integration_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    sync_service: FromDishka[CatalogSyncService],
) -> SyncResultResponse:
    tenant_id = _tenant(payload)
    result = await sync_service.sync_integration(
        integration_id=integration_id, tenant_id=tenant_id
    )
    return SyncResultResponse(
        integration_id=result.integration_id,
        products_upserted=result.products_upserted,
        variants_upserted=result.variants_upserted,
        shops_synced=result.shops_synced,
    )
