"""Application error hierarchy + RFC 7807 Problem Details handlers."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse


class AppError(Exception):
    code: str = "app.error"
    status: int = 500
    message: str = "application error"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message
        if code:
            self.code = code
        if status:
            self.status = status
        self.details = details or {}


class DomainError(AppError):
    code = "domain.error"
    status = 409


class ValidationError(AppError):
    code = "validation.error"
    status = 422


class NotFoundError(AppError):
    code = "not_found"
    status = 404


class AuthError(AppError):
    code = "auth.error"
    status = 401


class ForbiddenError(AppError):
    code = "auth.forbidden"
    status = 403


class IntegrationError(AppError):
    code = "integration.error"
    status = 502


async def app_error_handler(request: Request, exc: AppError) -> ORJSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    body: dict[str, Any] = {
        "type": f"https://anasklad.uz/errors/{exc.code}",
        "title": exc.message,
        "status": exc.status,
        "code": exc.code,
        "detail": exc.message,
    }
    if exc.details:
        body["details"] = exc.details
    if correlation_id:
        body["correlation_id"] = correlation_id
    return ORJSONResponse(
        status_code=exc.status,
        content=body,
        media_type="application/problem+json",
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
