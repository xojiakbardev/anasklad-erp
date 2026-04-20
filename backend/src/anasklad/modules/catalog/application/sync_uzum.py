"""Use-case: sync Uzum catalog for one integration.

Paginated, chunked, idempotent. Can be called by:
- Arq background job (scheduled)
- REST endpoint (manual "sync now")
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from uzum_connector import ClientConfig, UzumClient

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.http.errors import NotFoundError
from anasklad.modules.catalog.infrastructure.repository import (
    ProductRepository,
    VariantRepository,
)
from anasklad.modules.integrations.facade import IntegrationsFacade
from anasklad.modules.integrations.infrastructure.repository import (
    IntegrationRepository,
    ShopRepository,
)

logger = logging.getLogger("anasklad.catalog.sync")


@dataclass(slots=True, frozen=True)
class SyncResult:
    integration_id: uuid.UUID
    products_upserted: int
    variants_upserted: int
    shops_synced: int


class CatalogSyncService:
    def __init__(
        self,
        uow: UnitOfWork,
        products: ProductRepository,
        variants: VariantRepository,
        integrations_repo: IntegrationRepository,
        shop_repo: ShopRepository,
        integrations_facade: IntegrationsFacade,
    ) -> None:
        self._uow = uow
        self._products = products
        self._variants = variants
        self._integrations = integrations_repo
        self._shops = shop_repo
        self._facade = integrations_facade

    async def sync_integration(
        self, *, integration_id: uuid.UUID, tenant_id: uuid.UUID, page_size: int = 50
    ) -> SyncResult:
        integration = await self._integrations.get(integration_id, tenant_id)
        if integration is None:
            raise NotFoundError("integration not found")

        token = await self._facade.get_decrypted_token(
            integration_id=integration_id, tenant_id=tenant_id
        )
        if token is None:
            raise NotFoundError("integration credential not found")

        shops = await self._shops.list_for_integration(integration_id, tenant_id)
        products_upserted = 0
        variants_upserted = 0

        async with UzumClient(ClientConfig(token=token)) as client:
            for shop in shops:
                page = 0
                while True:
                    result = await client.list_products(
                        shop_id=shop.external_id, page=page, size=page_size
                    )
                    if not result.product_list:
                        break

                    # Process one page in a single DB transaction (chunked).
                    async with self._uow:
                        for product in result.product_list:
                            commission: float | None = None
                            if product.commission_dto:
                                commission = product.commission_dto.max_commission
                            elif product.commission is not None:
                                commission = product.commission

                            product_id = await self._products.upsert_from_uzum(
                                tenant_id=tenant_id,
                                integration_id=integration_id,
                                shop_id=shop.id,
                                external_id=product.product_id,
                                title=product.title or f"Product #{product.product_id}",
                                category=product.category,
                                image_url=product.image or product.preview_img,
                                rating=product.rating,
                                commission_percent=commission,
                            )
                            products_upserted += 1

                            for sku in product.sku_list:
                                await self._variants.upsert_from_uzum(
                                    tenant_id=tenant_id,
                                    product_id=product_id,
                                    external_id=sku.sku_id,
                                    title=sku.sku_title or sku.sku_full_title or "",
                                    barcode=str(sku.barcode) if sku.barcode else None,
                                    article=sku.article,
                                    seller_item_code=sku.seller_item_code,
                                    ikpu=sku.ikpu,
                                    characteristics=sku.characteristics,
                                    price=sku.price,
                                    purchase_price=sku.purchase_price,
                                    commission_percent=sku.commission,
                                    archived=bool(sku.archived),
                                    blocked=bool(sku.blocked),
                                    qty_fbo=sku.quantity_active or 0,
                                    qty_fbs=sku.quantity_fbs or 0,
                                    qty_sold_total=sku.quantity_sold or 0,
                                    qty_returned_total=sku.quantity_returned or 0,
                                    returned_percentage=sku.returned_percentage,
                                    preview_image_url=sku.preview_image,
                                )
                                variants_upserted += 1
                        await self._uow.commit()

                    logger.info(
                        "catalog.sync.page",
                        extra={
                            "integration_id": str(integration_id),
                            "shop_id": shop.external_id,
                            "page": page,
                            "count": len(result.product_list),
                        },
                    )

                    if len(result.product_list) < page_size:
                        break
                    page += 1
                    if page > 500:  # safety cap
                        break

        # Mark integration healthy.
        async with self._uow:
            await self._integrations.mark_ok(integration_id)
            await self._uow.commit()

        return SyncResult(
            integration_id=integration_id,
            products_upserted=products_upserted,
            variants_upserted=variants_upserted,
            shops_synced=len(shops),
        )
