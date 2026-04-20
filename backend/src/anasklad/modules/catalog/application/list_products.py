"""Query: list products with filter/sort/pagination."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from anasklad.modules.catalog.domain.entities import ProductListRow
from anasklad.modules.catalog.infrastructure.repository import ProductRepository


@dataclass(slots=True, frozen=True)
class ProductListQuery:
    tenant_id: uuid.UUID
    shop_id: uuid.UUID | None = None
    search: str | None = None
    page: int = 0
    size: int = 50


@dataclass(slots=True, frozen=True)
class ProductListResult:
    items: list[ProductListRow]
    total: int
    page: int
    size: int


class ProductListHandler:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    async def __call__(self, query: ProductListQuery) -> ProductListResult:
        items, total = await self._repo.list_rows(
            tenant_id=query.tenant_id,
            shop_id=query.shop_id,
            search=query.search,
            page=query.page,
            size=query.size,
        )
        return ProductListResult(items=items, total=total, page=query.page, size=query.size)
