"""Catalog repositories — products + variants."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.catalog.domain.entities import ProductListRow
from anasklad.modules.catalog.infrastructure.models import ProductModel, VariantModel


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_from_uzum(
        self,
        *,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        shop_id: uuid.UUID,
        external_id: int,
        title: str,
        category: str | None,
        image_url: str | None,
        rating: str | None,
        commission_percent: float | None,
    ) -> uuid.UUID:
        stmt = pg_insert(ProductModel).values(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            source="uzum",
            integration_id=integration_id,
            shop_id=shop_id,
            external_id=external_id,
            title=title,
            category=category,
            image_url=image_url,
            rating=rating,
            commission_percent=commission_percent,
            updated_at=datetime.now(UTC),
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_products_tenant_source_external",
            set_={
                "title": stmt.excluded.title,
                "category": stmt.excluded.category,
                "image_url": stmt.excluded.image_url,
                "rating": stmt.excluded.rating,
                "commission_percent": stmt.excluded.commission_percent,
                "integration_id": stmt.excluded.integration_id,
                "shop_id": stmt.excluded.shop_id,
                "updated_at": datetime.now(UTC),
            },
        ).returning(ProductModel.id)
        row = await self._session.execute(stmt)
        return row.scalar_one()

    async def list_rows(
        self,
        *,
        tenant_id: uuid.UUID,
        shop_id: uuid.UUID | None,
        search: str | None,
        page: int,
        size: int,
    ) -> tuple[list[ProductListRow], int]:
        base = (
            select(
                ProductModel.id,
                ProductModel.external_id,
                ProductModel.title,
                ProductModel.category,
                ProductModel.image_url,
                ProductModel.updated_at,
                func.count(VariantModel.id).label("sku_count"),
                func.coalesce(func.sum(VariantModel.qty_fbo), 0).label("qty_fbo_total"),
                func.coalesce(func.sum(VariantModel.qty_fbs), 0).label("qty_fbs_total"),
                func.min(VariantModel.price).label("min_price"),
                func.max(VariantModel.price).label("max_price"),
            )
            .outerjoin(VariantModel, VariantModel.product_id == ProductModel.id)
            .where(ProductModel.tenant_id == tenant_id)
            .group_by(
                ProductModel.id,
                ProductModel.external_id,
                ProductModel.title,
                ProductModel.category,
                ProductModel.image_url,
                ProductModel.updated_at,
            )
        )
        if shop_id is not None:
            base = base.where(ProductModel.shop_id == shop_id)
        if search:
            base = base.where(ProductModel.title.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        rows = (
            await self._session.execute(
                base.order_by(ProductModel.updated_at.desc())
                .limit(size)
                .offset(page * size)
            )
        ).all()

        result = [
            ProductListRow(
                product_id=r.id,
                external_id=r.external_id,
                title=r.title,
                category=r.category,
                image_url=r.image_url,
                sku_count=int(r.sku_count or 0),
                qty_fbo_total=int(r.qty_fbo_total or 0),
                qty_fbs_total=int(r.qty_fbs_total or 0),
                min_price=int(r.min_price) if r.min_price is not None else None,
                max_price=int(r.max_price) if r.max_price is not None else None,
                updated_at=r.updated_at,
            )
            for r in rows
        ]
        return result, int(total)

    async def count_for_tenant(self, tenant_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(ProductModel).where(ProductModel.tenant_id == tenant_id)
        return (await self._session.execute(stmt)).scalar_one()


class VariantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_from_uzum(
        self,
        *,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
        external_id: int,
        title: str,
        barcode: str | None,
        article: str | None,
        seller_item_code: str | None,
        ikpu: str | None,
        characteristics: str | None,
        price: int | None,
        purchase_price: int | None,
        commission_percent: float | None,
        archived: bool,
        blocked: bool,
        qty_fbo: int,
        qty_fbs: int,
        qty_sold_total: int,
        qty_returned_total: int,
        returned_percentage: float | None,
        preview_image_url: str | None,
    ) -> None:
        stmt = pg_insert(VariantModel).values(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            source="uzum",
            product_id=product_id,
            external_id=external_id,
            title=title,
            barcode=barcode,
            article=article,
            seller_item_code=seller_item_code,
            ikpu=ikpu,
            characteristics=characteristics,
            price=price,
            purchase_price=purchase_price,
            commission_percent=commission_percent,
            archived=archived,
            blocked=blocked,
            qty_fbo=qty_fbo,
            qty_fbs=qty_fbs,
            qty_sold_total=qty_sold_total,
            qty_returned_total=qty_returned_total,
            returned_percentage=returned_percentage,
            preview_image_url=preview_image_url,
            updated_at=datetime.now(UTC),
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_variants_tenant_source_external",
            set_={
                "title": stmt.excluded.title,
                "barcode": stmt.excluded.barcode,
                "article": stmt.excluded.article,
                "seller_item_code": stmt.excluded.seller_item_code,
                "ikpu": stmt.excluded.ikpu,
                "characteristics": stmt.excluded.characteristics,
                "price": stmt.excluded.price,
                "purchase_price": stmt.excluded.purchase_price,
                "commission_percent": stmt.excluded.commission_percent,
                "archived": stmt.excluded.archived,
                "blocked": stmt.excluded.blocked,
                "qty_fbo": stmt.excluded.qty_fbo,
                "qty_fbs": stmt.excluded.qty_fbs,
                "qty_sold_total": stmt.excluded.qty_sold_total,
                "qty_returned_total": stmt.excluded.qty_returned_total,
                "returned_percentage": stmt.excluded.returned_percentage,
                "preview_image_url": stmt.excluded.preview_image_url,
                "updated_at": datetime.now(UTC),
            },
        )
        await self._session.execute(stmt)

    async def list_for_product(
        self, *, tenant_id: uuid.UUID, product_id: uuid.UUID
    ) -> list[VariantModel]:
        stmt = (
            select(VariantModel)
            .where(
                and_(
                    VariantModel.tenant_id == tenant_id,
                    VariantModel.product_id == product_id,
                )
            )
            .order_by(VariantModel.title)
        )
        return list((await self._session.execute(stmt)).scalars().all())
