"""Integration domain entities — marketplace-agnostic."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class MarketplaceSource(StrEnum):
    UZUM = "uzum"
    WILDBERRIES = "wb"  # placeholder
    YANDEX = "yandex"  # placeholder


class IntegrationStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"  # last sync or token check failed


@dataclass(slots=True)
class Integration:
    id: UUID
    tenant_id: UUID
    source: MarketplaceSource
    label: str
    status: IntegrationStatus
    created_at: datetime
    last_checked_at: datetime | None
    last_error: str | None


@dataclass(slots=True)
class Shop:
    id: UUID
    integration_id: UUID
    tenant_id: UUID
    external_id: int  # Uzum shop id
    name: str
    created_at: datetime
