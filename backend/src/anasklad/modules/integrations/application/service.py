"""Integration use-cases."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from uzum_connector import (
    ClientConfig,
    UzumAuthError,
    UzumClient,
    UzumError,
)

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.http.errors import (
    AuthError,
    IntegrationError,
    NotFoundError,
    ValidationError,
)
from anasklad.core.security.crypto import CryptoService
from anasklad.modules.integrations.domain.entities import (
    Integration,
    MarketplaceSource,
    Shop,
)
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)


@dataclass(slots=True, frozen=True)
class IntegrationWithShops:
    integration: Integration
    shops: list[Shop]


class IntegrationService:
    def __init__(
        self,
        uow: UnitOfWork,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        crypto: CryptoService,
    ) -> None:
        self._uow = uow
        self._integrations = integrations
        self._shops = shops
        self._crypto = crypto

    async def list_for_tenant(self, tenant_id: uuid.UUID) -> list[IntegrationWithShops]:
        integrations = await self._integrations.list_for_tenant(tenant_id)
        result: list[IntegrationWithShops] = []
        for it in integrations:
            shops = await self._shops.list_for_integration(it.id, tenant_id)
            result.append(IntegrationWithShops(integration=it, shops=shops))
        return result

    async def connect_uzum(
        self, *, tenant_id: uuid.UUID, token: str, label: str
    ) -> IntegrationWithShops:
        if not token or len(token) < 16:
            raise ValidationError("token looks invalid (too short)", code="integration.bad_token")
        if not label or len(label) > 128:
            raise ValidationError("label must be 1-128 characters")

        # 1. Validate the token by calling /v1/shops BEFORE writing anything to DB.
        try:
            async with UzumClient(ClientConfig(token=token)) as client:
                shop_list = await client.list_shops()
        except UzumAuthError as e:
            raise AuthError("Uzum token is invalid or expired", code="integration.uzum.auth") from e
        except UzumError as e:
            raise IntegrationError(
                f"Uzum API error while validating token: {e.message}",
                code="integration.uzum.error",
            ) from e

        if not shop_list:
            raise ValidationError(
                "token is valid but no shops are associated with this seller",
                code="integration.uzum.no_shops",
            )

        # 2. Persist integration + shops atomically.
        encrypted = self._crypto.encrypt(token)
        async with self._uow:
            integration = await self._integrations.add(
                tenant_id=tenant_id,
                source=MarketplaceSource.UZUM,
                label=label,
                credentials_encrypted=encrypted,
            )
            shops = await self._shops.upsert_many(
                integration_id=integration.id,
                tenant_id=tenant_id,
                shops=[(s.id, s.name or f"Shop #{s.id}") for s in shop_list],
            )
            await self._integrations.mark_ok(integration.id)
            await self._uow.commit()

        return IntegrationWithShops(integration=integration, shops=shops)

    async def delete(self, *, tenant_id: uuid.UUID, integration_id: uuid.UUID) -> None:
        async with self._uow:
            existed = await self._integrations.get(integration_id, tenant_id)
            if existed is None:
                raise NotFoundError("integration not found")
            await self._integrations.delete(integration_id, tenant_id)
            await self._uow.commit()

    async def test(self, *, tenant_id: uuid.UUID, integration_id: uuid.UUID) -> IntegrationWithShops:
        integration = await self._integrations.get(integration_id, tenant_id)
        if integration is None:
            raise NotFoundError("integration not found")

        raw = await self._integrations.get_credential_raw(integration_id, tenant_id)
        if not raw:
            raise IntegrationError("integration has no stored credentials")
        token = self._crypto.decrypt(raw)

        async with self._uow:
            try:
                async with UzumClient(ClientConfig(token=token)) as client:
                    shop_list = await client.list_shops()
            except UzumError as e:
                await self._integrations.mark_error(integration_id, e.message)
                await self._uow.commit()
                raise IntegrationError(
                    f"Uzum connection failed: {e.message}",
                    code="integration.uzum.error",
                ) from e

            shops = await self._shops.upsert_many(
                integration_id=integration_id,
                tenant_id=tenant_id,
                shops=[(s.id, s.name or f"Shop #{s.id}") for s in shop_list],
            )
            await self._integrations.mark_ok(integration_id)
            await self._uow.commit()
            refreshed = await self._integrations.get(integration_id, tenant_id)
            assert refreshed is not None
            return IntegrationWithShops(integration=refreshed, shops=shops)
