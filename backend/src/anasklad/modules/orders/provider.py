"""Dishka provider for orders module."""
from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.core.db.uow import UnitOfWork
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)
from anasklad.modules.orders.application.service import OrderService
from anasklad.modules.orders.infrastructure.repository import FbsOrderRepository


class OrdersProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def order_repo(self, session: AsyncSession) -> FbsOrderRepository:
        return FbsOrderRepository(session)

    @provide
    def order_service(
        self,
        uow: UnitOfWork,
        orders: FbsOrderRepository,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        facade: IntegrationsFacade,
    ) -> OrderService:
        return OrderService(uow, orders, integrations, shops, facade)
