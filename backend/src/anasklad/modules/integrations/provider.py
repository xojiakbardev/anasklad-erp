"""Dishka provider for the integrations module."""
from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.security.crypto import CryptoService
from anasklad.modules.integrations.application.service import IntegrationService
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)


class IntegrationsProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def integration_repo(self, session: AsyncSession) -> IntegrationRepository:
        return IntegrationRepository(session)

    @provide
    def shop_repo(self, session: AsyncSession) -> ShopRepository:
        return ShopRepository(session)

    @provide
    def integration_service(
        self,
        uow: UnitOfWork,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        crypto: CryptoService,
    ) -> IntegrationService:
        return IntegrationService(uow, integrations, shops, crypto)

    @provide
    def facade(
        self,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        crypto: CryptoService,
    ) -> IntegrationsFacade:
        return IntegrationsFacade(integrations, shops, crypto)
