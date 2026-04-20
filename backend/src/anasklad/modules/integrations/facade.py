"""Public facade — what OTHER modules may use.

Only read-only accessors + decrypted token delivery for sync workers.
Never expose ORM or application-layer side effects.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from anasklad.core.security.crypto import CryptoService
from anasklad.modules.integrations.domain.entities import MarketplaceSource
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)


@dataclass(slots=True, frozen=True)
class IntegrationRef:
    id: uuid.UUID
    tenant_id: uuid.UUID
    source: MarketplaceSource
    label: str
    rate_per_second: float
    rate_burst: int


@dataclass(slots=True, frozen=True)
class ShopRef:
    id: uuid.UUID
    tenant_id: uuid.UUID
    integration_id: uuid.UUID
    external_id: int
    name: str


class IntegrationsFacade:
    def __init__(
        self,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        crypto: CryptoService,
    ) -> None:
        self._integrations = integrations
        self._shops = shops
        self._crypto = crypto

    async def get_decrypted_token(
        self, *, integration_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> str | None:
        raw = await self._integrations.get_credential_raw(integration_id, tenant_id)
        if not raw:
            return None
        return self._crypto.decrypt(raw)

    async def list_shops_for_tenant(self, tenant_id: uuid.UUID) -> list[ShopRef]:
        shops = await self._shops.list_for_tenant(tenant_id)
        return [
            ShopRef(
                id=s.id,
                tenant_id=s.tenant_id,
                integration_id=s.integration_id,
                external_id=s.external_id,
                name=s.name,
            )
            for s in shops
        ]
