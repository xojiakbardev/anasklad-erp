"""Shared FastAPI dependencies."""
from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import FromDishka
from fastapi import Header

from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import JwtService, TokenPayload


async def current_user(
    authorization: Annotated[str | None, Header()] = None,
    jwt_service: FromDishka[JwtService] = None,  # type: ignore[assignment]
) -> TokenPayload:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthError("missing bearer token", code="auth.missing_token")
    token = authorization.split(" ", 1)[1].strip()
    return jwt_service.verify(token, expected_type="access")
