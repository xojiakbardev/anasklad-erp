"""Shared response envelope and common DTOs."""
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True, str_strip_whitespace=True)


class ApiError(_Base):
    code: str
    message: str
    detail_message: str | None = Field(default=None, alias="detailMessage")
    payload: dict | None = None


class GenericResponse(_Base, Generic[T]):
    """Uzum's standard envelope: {payload, errors, timestamp, trace, error}."""

    payload: T | None = None
    errors: list[ApiError] = Field(default_factory=list)
    timestamp: datetime | None = None
    trace: str | None = None
    error: str | None = None

    @property
    def is_ok(self) -> bool:
        return not self.errors and self.error in (None, "null")


class PaginatedResponse(_Base, Generic[T]):
    """Generic paginated shape for endpoints that return {items, totalAmount}."""

    items: list[T]
    total: int


class Photo(_Base):
    high: str | None = None
    low: str | None = None
