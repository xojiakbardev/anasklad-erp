"""Integration API request/response schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ConnectUzumRequest(_Base):
    token: str = Field(min_length=16, max_length=512, description="Uzum seller API token")
    label: str = Field(min_length=1, max_length=128, description='Human-friendly label, e.g. "Main shop"')


class ShopResponse(_Base):
    id: UUID
    external_id: int
    name: str
    created_at: datetime


class IntegrationResponse(_Base):
    id: UUID
    source: str
    label: str
    status: str
    last_checked_at: datetime | None
    last_error: str | None
    created_at: datetime
    shops: list[ShopResponse]
