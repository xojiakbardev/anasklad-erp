"""Dishka provider for the catalog module."""
from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.core.db.uow import UnitOfWork
from anasklad.modules.catalog.application.list_products import ProductListHandler
from anasklad.modules.catalog.application.sync_uzum import CatalogSyncService
from anasklad.modules.catalog.infrastructure.repository import (
    ProductRepository,
    VariantRepository,
)
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)


class CatalogProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def product_repo(self, session: AsyncSession) -> ProductRepository:
        return ProductRepository(session)

    @provide
    def variant_repo(self, session: AsyncSession) -> VariantRepository:
        return VariantRepository(session)

    @provide
    def list_products_handler(self, repo: ProductRepository) -> ProductListHandler:
        return ProductListHandler(repo)

    @provide
    def sync_service(
        self,
        uow: UnitOfWork,
        products: ProductRepository,
        variants: VariantRepository,
        integrations_repo: IntegrationRepository,
        shop_repo: ShopRepository,
        facade: IntegrationsFacade,
    ) -> CatalogSyncService:
        return CatalogSyncService(
            uow, products, variants, integrations_repo, shop_repo, facade
        )
