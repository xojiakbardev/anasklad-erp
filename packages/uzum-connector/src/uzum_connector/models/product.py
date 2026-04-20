"""Product / SKU DTOs — /v1/product/shop/{shopId}."""
from __future__ import annotations

from pydantic import Field

from uzum_connector.models.common import _Base


class Commission(_Base):
    min_commission: float | None = Field(default=None, alias="minCommission")
    max_commission: float | None = Field(default=None, alias="maxCommission")


class Sku(_Base):
    sku_id: int = Field(alias="skuId")
    sku_title: str | None = Field(default=None, alias="skuTitle")
    sku_full_title: str | None = Field(default=None, alias="skuFullTitle")
    product_title: str | None = Field(default=None, alias="productTitle")
    barcode: int | None = None
    article: str | None = None
    seller_item_code: str | None = Field(default=None, alias="sellerItemCode")
    ikpu: str | None = None

    quantity_created: int | None = Field(default=None, alias="quantityCreated")
    quantity_active: int | None = Field(default=None, alias="quantityActive")
    quantity_fbs: int | None = Field(default=None, alias="quantityFbs")
    quantity_archived: int | None = Field(default=None, alias="quantityArchived")
    quantity_sold: int | None = Field(default=None, alias="quantitySold")
    quantity_returned: int | None = Field(default=None, alias="quantityReturned")
    quantity_defected: int | None = Field(default=None, alias="quantityDefected")
    quantity_pending: int | None = Field(default=None, alias="quantityPending")
    returned_percentage: float | None = Field(default=None, alias="returnedPercentage")

    purchase_price: int | None = Field(default=None, alias="purchasePrice")
    price: int | None = None
    commission: float | None = None

    archived: bool | None = None
    blocked: bool | None = None
    blocking_reason: str | None = Field(default=None, alias="blockingReason")

    characteristics: str | None = None
    dimensional_group: str | None = Field(default=None, alias="dimensionalGroup")
    turnover: float | None = None
    preview_image: str | None = Field(default=None, alias="previewImage")


class Product(_Base):
    product_id: int = Field(alias="productId")
    title: str | None = None
    category: str | None = None
    rating: str | None = None
    image: str | None = None
    preview_img: str | None = Field(default=None, alias="previewImg")
    sku_title: str | None = Field(default=None, alias="skuTitle")

    commission: float | None = None
    commission_dto: Commission | None = Field(default=None, alias="commissionDto")

    quantity_active: int | None = Field(default=None, alias="quantityActive")
    quantity_fbs: int | None = Field(default=None, alias="quantityFbs")

    sku_list: list[Sku] = Field(default_factory=list, alias="skuList")


class ProductsPage(_Base):
    product_list: list[Product] = Field(default_factory=list, alias="productList")
    total: int = Field(default=0, alias="totalProductsAmount")
