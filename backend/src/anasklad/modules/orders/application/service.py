"""Order use-cases."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from uzum_connector import ClientConfig, UzumClient
from uzum_connector.models import FbsOrderStatus

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.http.errors import IntegrationError, NotFoundError
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)
from anasklad.modules.orders.domain.enums import KANBAN_COLUMNS
from anasklad.modules.orders.infrastructure.models import (
    FbsOrderItemModel,
    FbsOrderModel,
)
from anasklad.modules.orders.infrastructure.repository import FbsOrderRepository


@dataclass(slots=True, frozen=True)
class SyncResult:
    orders_upserted: int
    shops_synced: int


class OrderService:
    def __init__(
        self,
        uow: UnitOfWork,
        orders: FbsOrderRepository,
        integrations_repo: IntegrationRepository,
        shop_repo: ShopRepository,
        facade: IntegrationsFacade,
    ) -> None:
        self._uow = uow
        self._orders = orders
        self._integrations = integrations_repo
        self._shops = shop_repo
        self._facade = facade

    async def list(
        self,
        *,
        tenant_id: uuid.UUID,
        status: str | None,
        shop_id: uuid.UUID | None,
        page: int,
        size: int,
    ) -> tuple[list[FbsOrderModel], int]:
        return await self._orders.list(
            tenant_id=tenant_id, status=status, shop_id=shop_id, page=page, size=size
        )

    async def counts(self, *, tenant_id: uuid.UUID) -> dict[str, int]:
        return await self._orders.counts_by_status(
            tenant_id=tenant_id, statuses=[s.value for s in KANBAN_COLUMNS]
        )

    async def get(
        self, *, tenant_id: uuid.UUID, order_id: uuid.UUID
    ) -> tuple[FbsOrderModel, list[FbsOrderItemModel]]:
        order = await self._orders.get(order_id, tenant_id)
        if order is None:
            raise NotFoundError("order not found")
        items = await self._orders.get_items(order_id, tenant_id)
        return order, items

    async def sync(
        self, *, tenant_id: uuid.UUID, integration_id: uuid.UUID
    ) -> SyncResult:
        integration = await self._integrations.get(integration_id, tenant_id)
        if integration is None:
            raise NotFoundError("integration not found")
        token = await self._facade.get_decrypted_token(
            integration_id=integration_id, tenant_id=tenant_id
        )
        if not token:
            raise NotFoundError("integration credentials missing")

        shops = await self._shops.list_for_integration(integration_id, tenant_id)
        shop_by_external: dict[int, uuid.UUID] = {s.external_id: s.id for s in shops}
        orders_upserted = 0

        async with UzumClient(ClientConfig(token=token)) as client:
            for status in KANBAN_COLUMNS:
                page = 0
                while True:
                    result = await client.list_fbs_orders(
                        shop_ids=[s.external_id for s in shops],
                        status=FbsOrderStatus(status.value),
                        page=page,
                        size=50,
                    )
                    if not result.orders:
                        break

                    async with self._uow:
                        for o in result.orders:
                            ext_shop = o.shop_id
                            if ext_shop is None:
                                continue
                            internal_shop = shop_by_external.get(ext_shop)
                            if internal_shop is None:
                                continue

                            order_id = await self._orders.upsert_from_uzum(
                                tenant_id=tenant_id,
                                integration_id=integration_id,
                                shop_id=internal_shop,
                                fields={
                                    "external_id": o.id,
                                    "external_shop_id": ext_shop,
                                    "invoice_number": o.invoice_number,
                                    "status": o.status.value,
                                    "scheme": o.scheme.value if o.scheme else None,
                                    "price": o.price,
                                    "cancel_reason": o.cancel_reason,
                                    "date_created": o.date_created,
                                    "accept_until": o.accept_until,
                                    "deliver_until": o.deliver_until,
                                    "accepted_date": o.accepted_date,
                                    "delivering_date": o.delivering_date,
                                    "delivery_date": o.delivery_date,
                                    "delivered_to_dp_date": o.delivered_to_dp_date,
                                    "completed_date": o.completed_date,
                                    "date_cancelled": o.date_cancelled,
                                    "return_date": o.return_date,
                                },
                            )
                            items = [
                                {
                                    "external_sku_id": it.sku_id,
                                    "sku_title": it.sku_title,
                                    "product_title": it.product_title,
                                    "amount": it.amount or 0,
                                    "seller_price": it.seller_price,
                                    "purchase_price": it.purchase_price,
                                    "commission": it.commission,
                                    "logistic_delivery_fee": it.logistic_delivery_fee,
                                    "seller_profit": it.seller_profit,
                                    "raw": json.dumps(it.model_dump(), default=str),
                                }
                                for it in o.order_items
                            ]
                            await self._orders.replace_items(
                                tenant_id=tenant_id, order_id=order_id, items=items
                            )
                            orders_upserted += 1
                        await self._uow.commit()

                    if len(result.orders) < 50:
                        break
                    page += 1
                    if page > 200:
                        break

        return SyncResult(orders_upserted=orders_upserted, shops_synced=len(shops))

    async def confirm(
        self, *, tenant_id: uuid.UUID, order_id: uuid.UUID
    ) -> FbsOrderModel:
        order = await self._orders.get(order_id, tenant_id)
        if order is None:
            raise NotFoundError("order not found")
        token = await self._facade.get_decrypted_token(
            integration_id=order.integration_id, tenant_id=tenant_id
        )
        if not token:
            raise NotFoundError("integration token missing")

        async with UzumClient(ClientConfig(token=token)) as client:
            try:
                updated = await client.confirm_fbs_order(order.external_id)
            except Exception as e:
                raise IntegrationError(f"confirm failed: {e}", code="orders.confirm_failed") from e

        async with self._uow:
            await self._orders.update_status(order_id, tenant_id, updated.status.value)
            await self._uow.commit()
        refreshed = await self._orders.get(order_id, tenant_id)
        assert refreshed is not None
        return refreshed

    async def cancel(
        self,
        *,
        tenant_id: uuid.UUID,
        order_id: uuid.UUID,
        reason: str,
        comment: str | None,
    ) -> FbsOrderModel:
        order = await self._orders.get(order_id, tenant_id)
        if order is None:
            raise NotFoundError("order not found")
        token = await self._facade.get_decrypted_token(
            integration_id=order.integration_id, tenant_id=tenant_id
        )
        if not token:
            raise NotFoundError("integration token missing")

        async with UzumClient(ClientConfig(token=token)) as client:
            try:
                await client.cancel_fbs_order(
                    order.external_id, reason=reason, comment=comment
                )
            except Exception as e:
                raise IntegrationError(f"cancel failed: {e}", code="orders.cancel_failed") from e

        async with self._uow:
            await self._orders.update_status(order_id, tenant_id, "CANCELED")
            await self._uow.commit()
        refreshed = await self._orders.get(order_id, tenant_id)
        assert refreshed is not None
        return refreshed

    async def label_pdf(
        self, *, tenant_id: uuid.UUID, order_id: uuid.UUID, size: str = "LARGE"
    ) -> bytes:
        order = await self._orders.get(order_id, tenant_id)
        if order is None:
            raise NotFoundError("order not found")
        token = await self._facade.get_decrypted_token(
            integration_id=order.integration_id, tenant_id=tenant_id
        )
        if not token:
            raise NotFoundError("integration token missing")

        async with UzumClient(ClientConfig(token=token)) as client:
            try:
                return await client.get_fbs_order_label(order.external_id, size=size)
            except Exception as e:
                raise IntegrationError(f"label failed: {e}", code="orders.label_failed") from e
