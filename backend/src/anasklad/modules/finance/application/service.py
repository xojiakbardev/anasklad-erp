"""Finance use-cases."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from uzum_connector import ClientConfig, UzumClient

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.http.errors import NotFoundError
from anasklad.modules.finance.infrastructure.models import ExpenseModel, SaleModel
from anasklad.modules.finance.infrastructure.repository import (
    ExpenseRepository,
    SaleRepository,
)
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)


@dataclass(slots=True, frozen=True)
class FinanceSyncResult:
    sales_upserted: int
    expenses_upserted: int


class FinanceService:
    def __init__(
        self,
        uow: UnitOfWork,
        sales: SaleRepository,
        expenses: ExpenseRepository,
        integrations: IntegrationRepository,
        shops: ShopRepository,
        facade: IntegrationsFacade,
    ) -> None:
        self._uow = uow
        self._sales = sales
        self._expenses = expenses
        self._integrations = integrations
        self._shops = shops
        self._facade = facade

    async def sync(
        self, *, tenant_id: uuid.UUID, integration_id: uuid.UUID, days_back: int = 30
    ) -> FinanceSyncResult:
        integration = await self._integrations.get(integration_id, tenant_id)
        if integration is None:
            raise NotFoundError("integration not found")
        token = await self._facade.get_decrypted_token(
            integration_id=integration_id, tenant_id=tenant_id
        )
        if not token:
            raise NotFoundError("integration credentials missing")

        shops = await self._shops.list_for_integration(integration_id, tenant_id)
        shop_by_external = {s.external_id: s.id for s in shops}
        date_to = datetime.now(UTC)
        date_from = date_to - timedelta(days=days_back)
        ms_from = int(date_from.timestamp() * 1000)
        ms_to = int(date_to.timestamp() * 1000)

        sales_upserted = 0
        expenses_upserted = 0

        async with UzumClient(ClientConfig(token=token)) as client:
            # --- Sales ---
            page = 0
            while True:
                result = await client.list_finance_orders(
                    shop_ids=[s.external_id for s in shops],
                    date_from_ms=ms_from,
                    date_to_ms=ms_to,
                    page=page,
                    size=50,
                )
                if not result.order_items:
                    break

                async with self._uow:
                    for item in result.order_items:
                        if item.id is None:
                            continue
                        internal_shop = (
                            shop_by_external.get(item.shop_id) if item.shop_id else None
                        )
                        await self._sales.upsert(
                            {
                                "tenant_id": tenant_id,
                                "integration_id": integration_id,
                                "shop_id": internal_shop,
                                "external_id": item.id,
                                "external_order_id": item.order_id,
                                "external_shop_id": item.shop_id,
                                "external_product_id": item.product_id,
                                "status": item.status.value if item.status else None,
                                "sold_at": item.date_dt,
                                "product_title": item.product_title,
                                "sku_title": item.sku_title,
                                "amount": item.amount or 0,
                                "amount_returns": item.amount_returns or 0,
                                "cancelled": item.cancelled or 0,
                                "seller_price": item.seller_price,
                                "purchase_price": item.purchase_price,
                                "commission": item.commission,
                                "logistic_delivery_fee": item.logistic_delivery_fee,
                                "seller_profit": item.seller_profit,
                                "withdrawn_profit": item.withdrawn_profit,
                                "return_cause": item.return_cause,
                            }
                        )
                        sales_upserted += 1
                    await self._uow.commit()

                if len(result.order_items) < 50:
                    break
                page += 1
                if page > 500:
                    break

            # --- Expenses ---
            page = 0
            while True:
                result = await client.list_finance_expenses(
                    shop_ids=[s.external_id for s in shops],
                    date_from_ms=ms_from,
                    date_to_ms=ms_to,
                    page=page,
                    size=100,
                )
                if not result.payments:
                    break
                async with self._uow:
                    for e in result.payments:
                        internal_shop = (
                            shop_by_external.get(e.shop_id) if e.shop_id else None
                        )
                        await self._expenses.upsert(
                            {
                                "tenant_id": tenant_id,
                                "integration_id": integration_id,
                                "shop_id": internal_shop,
                                "external_id": e.id,
                                "external_shop_id": e.shop_id,
                                "name": e.name,
                                "source_kind": e.source,
                                "type": e.type.value if e.type else None,
                                "status": e.status.value if e.status else None,
                                "payment_price": e.payment_price,
                                "amount": e.amount or 0,
                                "date_created": e.date_created,
                                "date_service": e.date_service,
                                "code": e.code,
                            }
                        )
                        expenses_upserted += 1
                    await self._uow.commit()
                if len(result.payments) < 100:
                    break
                page += 1
                if page > 200:
                    break

        return FinanceSyncResult(
            sales_upserted=sales_upserted, expenses_upserted=expenses_upserted
        )

    async def summary(
        self, *, tenant_id: uuid.UUID, period_days: int = 30
    ) -> dict:
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_start = now - timedelta(days=period_days)

        today = await self._sales.summary(
            tenant_id=tenant_id, date_from=today_start, date_to=now
        )
        period = await self._sales.summary(
            tenant_id=tenant_id, date_from=period_start, date_to=now
        )
        daily = await self._sales.daily_profit(
            tenant_id=tenant_id, date_from=period_start, date_to=now
        )
        top = await self._sales.top_products(
            tenant_id=tenant_id, date_from=period_start, date_to=now
        )
        return {
            "today": today,
            "period": period,
            "period_days": period_days,
            "daily": [
                {"day": d.isoformat(), "revenue": r, "profit": p} for d, r, p in daily
            ],
            "top_products": top,
        }

    async def list_sales(
        self, *, tenant_id: uuid.UUID, page: int, size: int
    ) -> tuple[list[SaleModel], int]:
        return await self._sales.list(tenant_id=tenant_id, page=page, size=size)

    async def list_expenses(
        self, *, tenant_id: uuid.UUID, page: int, size: int
    ) -> tuple[list[ExpenseModel], int]:
        return await self._expenses.list(tenant_id=tenant_id, page=page, size=size)
