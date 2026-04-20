"""Dishka provider for finance module."""
from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.core.db.uow import UnitOfWork
from anasklad.modules.finance.application.service import FinanceService
from anasklad.modules.finance.infrastructure.repository import (
    ExpenseRepository,
    SaleRepository,
)
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)


class FinanceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def sale_repo(self, session: AsyncSession) -> SaleRepository:
        return SaleRepository(session)

    @provide
    def expense_repo(self, session: AsyncSession) -> ExpenseRepository:
        return ExpenseRepository(session)

    @provide
    def finance_service(
        self,
        uow: UnitOfWork,
        sales: SaleRepository,
        expenses: ExpenseRepository,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        facade: IntegrationsFacade,
    ) -> FinanceService:
        return FinanceService(uow, sales, expenses, integrations, shops, facade)
