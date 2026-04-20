"""Integration HTTP endpoints."""
from __future__ import annotations

import uuid
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from anasklad.core.http.deps import current_user
from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import TokenPayload
from anasklad.modules.integrations.api.schemas import (
    ConnectUzumRequest,
    IntegrationResponse,
    ShopResponse,
)
from anasklad.modules.integrations.application.service import (
    IntegrationService,
    IntegrationWithShops,
)

router = APIRouter(prefix="/integrations", tags=["integrations"], route_class=DishkaRoute)


def _tenant_from_token(p: TokenPayload) -> uuid.UUID:
    if p.tenant_id is None:
        raise AuthError("token missing tenant claim", code="auth.missing_tenant")
    return uuid.UUID(p.tenant_id)


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[IntegrationService],
) -> list[IntegrationResponse]:
    tenant_id = _tenant_from_token(payload)
    items = await service.list_for_tenant(tenant_id)
    return [_to_response(i) for i in items]


@router.post("/uzum", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def connect_uzum(
    body: ConnectUzumRequest,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[IntegrationService],
) -> IntegrationResponse:
    tenant_id = _tenant_from_token(payload)
    result = await service.connect_uzum(tenant_id=tenant_id, token=body.token, label=body.label)
    return _to_response(result)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[IntegrationService],
) -> None:
    tenant_id = _tenant_from_token(payload)
    await service.delete(tenant_id=tenant_id, integration_id=integration_id)


@router.post("/{integration_id}/test", response_model=IntegrationResponse)
async def test_integration(
    integration_id: uuid.UUID,
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[IntegrationService],
) -> IntegrationResponse:
    tenant_id = _tenant_from_token(payload)
    result = await service.test(tenant_id=tenant_id, integration_id=integration_id)
    return _to_response(result)


def _to_response(item: IntegrationWithShops) -> IntegrationResponse:
    return IntegrationResponse(
        id=item.integration.id,
        source=item.integration.source.value,
        label=item.integration.label,
        status=item.integration.status.value,
        last_checked_at=item.integration.last_checked_at,
        last_error=item.integration.last_error,
        created_at=item.integration.created_at,
        shops=[
            ShopResponse(
                id=s.id,
                external_id=s.external_id,
                name=s.name,
                created_at=s.created_at,
            )
            for s in item.shops
        ],
    )
