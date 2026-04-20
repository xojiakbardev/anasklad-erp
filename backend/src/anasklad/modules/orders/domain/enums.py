"""Status + scheme enums for FBS/FBO orders."""
from __future__ import annotations

from enum import StrEnum


class FbsStatus(StrEnum):
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


class OrderScheme(StrEnum):
    FBS = "FBS"
    DBS = "DBS"
    FBO = "FBO"


# Kanban board order — 5 visible columns, rest as "history"
KANBAN_COLUMNS: list[FbsStatus] = [
    FbsStatus.CREATED,
    FbsStatus.PACKING,
    FbsStatus.PENDING_DELIVERY,
    FbsStatus.DELIVERING,
    FbsStatus.DELIVERED,
]


CANCEL_REASONS = [
    "OUT_OF_STOCK",
    "OUT_OF_PACKAGE",
    "OUT_OF_TIME",
    "OTHER",
]
