"""Exception hierarchy for the Uzum client."""
from __future__ import annotations

from typing import Any


class UzumError(Exception):
    """Base class for all Uzum client errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        payload: Any = None,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.payload = payload
        self.correlation_id = correlation_id

    def __repr__(self) -> str:
        parts = [f"status={self.status_code}", f"code={self.code!r}"]
        if self.correlation_id:
            parts.append(f"correlation_id={self.correlation_id!r}")
        return f"{type(self).__name__}({self.message!r}, {', '.join(parts)})"


class UzumAuthError(UzumError):
    """401/403 — token invalid, expired, or lacks permission."""


class UzumNotFoundError(UzumError):
    """404 — resource does not exist."""


class UzumValidationError(UzumError):
    """400 — request rejected by validation."""


class UzumRateLimitError(UzumError):
    """429 — rate limited. Check `retry_after_seconds`."""

    def __init__(self, message: str, *, retry_after_seconds: float | None = None, **kw: Any) -> None:
        super().__init__(message, **kw)
        self.retry_after_seconds = retry_after_seconds


class UzumServerError(UzumError):
    """5xx — upstream service error, retryable."""


class UzumTransportError(UzumError):
    """Network/transport error (timeout, connection reset, DNS)."""
