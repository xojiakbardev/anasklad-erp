"""Finance DTOs — /v1/finance/orders and /v1/finance/expenses."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from uzum_connector.models.common import _Base


class FinanceOrderStatus(StrEnum):
    TO_WITHDRAW = "TO_WITHDRAW"
    PROCESSING = "PROCESSING"
    CANCELED = "CANCELED"
    PARTIALLY_CANCELLED = "PARTIALLY_CANCELLED"


class FinanceOrderItem(_Base):
    """Single (flat) seller order item — matches SellerOrderItemDto when group=false."""

    id: int | None = None
    status: FinanceOrderStatus | None = None
    date: int | None = None  # epoch ms
    order_id: int | None = Field(default=None, alias="orderId")
    shop_id: int | None = Field(default=None, alias="shopId")
    product_id: int | None = Field(default=None, alias="productId")
    product_title: str | None = Field(default=None, alias="productTitle")
    sku_title: str | None = Field(default=None, alias="skuTitle")

    amount: int | None = None
    amount_returns: int | None = Field(default=None, alias="amountReturns")
    cancelled: int | None = None

    seller_price: int | None = Field(default=None, alias="sellerPrice")
    purchase_price: int | None = Field(default=None, alias="purchasePrice")
    commission: int | None = None
    logistic_delivery_fee: int | None = Field(default=None, alias="logisticDeliveryFee")
    seller_profit: int | None = Field(default=None, alias="sellerProfit")
    withdrawn_profit: int | None = Field(default=None, alias="withdrawnProfit")
    return_cause: str | None = Field(default=None, alias="returnCause")
    comment: str | None = None
    sku_char_value: str | None = Field(default=None, alias="skuCharValue")
    sku_char_title: str | None = Field(default=None, alias="skuCharTitle")

    @property
    def date_dt(self) -> datetime | None:
        return datetime.fromtimestamp(self.date / 1000) if self.date else None


class FinanceOrderItemsPage(_Base):
    order_items: list[FinanceOrderItem] = Field(default_factory=list, alias="orderItems")
    total: int = Field(default=0, alias="totalElements")


class ExpenseType(StrEnum):
    INCOME = "INCOME"
    OUTCOME = "OUTCOME"


class ExpenseStatus(StrEnum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    REFUNDED = "REFUNDED"
    CANCELED = "CANCELED"


class SellerExpense(_Base):
    id: int
    date_created: datetime | None = Field(default=None, alias="dateCreated")
    date_updated: datetime | None = Field(default=None, alias="dateUpdated")
    date_service: datetime | None = Field(default=None, alias="dateService")
    name: str | None = None
    source: str | None = None
    shop_id: int | None = Field(default=None, alias="shopId")
    seller_id: int | None = Field(default=None, alias="sellerId")
    payment_price: int | None = Field(default=None, alias="paymentPrice")
    amount: int | None = None
    status: ExpenseStatus | None = None
    external_id: str | None = Field(default=None, alias="externalId")
    code: str | None = None
    type: ExpenseType | None = None


class SellerExpensesPage(_Base):
    payments: list[SellerExpense] = Field(default_factory=list)
