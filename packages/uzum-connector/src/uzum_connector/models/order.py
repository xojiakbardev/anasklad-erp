"""FBS order DTOs — /v2/fbs/orders."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from uzum_connector.models.common import _Base


class FbsOrderStatus(StrEnum):
    CREATED = "CREATED"
    PACKING = "PACKING"
    PENDING_DELIVERY = "PENDING_DELIVERY"
    DELIVERING = "DELIVERING"
    DELIVERED = "DELIVERED"
    ACCEPTED_AT_DP = "ACCEPTED_AT_DP"
    DELIVERED_TO_CUSTOMER_DELIVERY_POINT = "DELIVERED_TO_CUSTOMER_DELIVERY_POINT"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    PENDING_CANCELLATION = "PENDING_CANCELLATION"
    RETURNED = "RETURNED"


class FbsOrderScheme(StrEnum):
    FBS = "FBS"
    DBS = "DBS"
    FBO = "FBO"


class FbsOrderItem(_Base):
    id: int | None = None
    sku_id: int | None = Field(default=None, alias="skuId")
    sku_title: str | None = Field(default=None, alias="skuTitle")
    product_id: int | None = Field(default=None, alias="productId")
    product_title: str | None = Field(default=None, alias="productTitle")
    amount: int | None = None
    seller_price: int | None = Field(default=None, alias="sellerPrice")
    purchase_price: int | None = Field(default=None, alias="purchasePrice")
    commission: int | None = None
    logistic_delivery_fee: int | None = Field(default=None, alias="logisticDeliveryFee")
    seller_profit: int | None = Field(default=None, alias="sellerProfit")


class FbsOrder(_Base):
    id: int
    status: FbsOrderStatus
    scheme: FbsOrderScheme | None = None

    shop_id: int | None = Field(default=None, alias="shopId")
    price: int | None = None
    invoice_number: int | None = Field(default=None, alias="invoiceNumber")
    cancel_reason: str | None = Field(default=None, alias="cancelReason")

    date_created: datetime | None = Field(default=None, alias="dateCreated")
    accept_until: datetime | None = Field(default=None, alias="acceptUntil")
    deliver_until: datetime | None = Field(default=None, alias="deliverUntil")
    accepted_date: datetime | None = Field(default=None, alias="acceptedDate")
    delivering_date: datetime | None = Field(default=None, alias="deliveringDate")
    delivery_date: datetime | None = Field(default=None, alias="deliveryDate")
    delivered_to_dp_date: datetime | None = Field(default=None, alias="deliveredToDeliveryPointDate")
    completed_date: datetime | None = Field(default=None, alias="completedDate")
    date_cancelled: datetime | None = Field(default=None, alias="dateCancelled")
    return_date: datetime | None = Field(default=None, alias="returnDate")

    order_items: list[FbsOrderItem] = Field(default_factory=list, alias="orderItems")


class FbsOrdersPage(_Base):
    orders: list[FbsOrder] = Field(default_factory=list)
    total: int = Field(default=0, alias="totalAmount")
