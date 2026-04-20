"""Catalog facade — keeps it minimal for now."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from anasklad.modules.catalog.infrastructure.repository import ProductRepository


@dataclass(slots=True, frozen=True)
class ProductCount:
    tenant_id: uuid.UUID
    count: int


class CatalogFacade:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    async def product_count(self, tenant_id: uuid.UUID) -> ProductCount:
        return ProductCount(tenant_id=tenant_id, count=await self._products.count_for_tenant(tenant_id))
