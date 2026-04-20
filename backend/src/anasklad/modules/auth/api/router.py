"""Auth HTTP endpoints."""
from __future__ import annotations

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from anasklad.core.http.deps import current_user
from anasklad.core.security.jwt import TokenPayload
from anasklad.modules.auth.api.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from anasklad.modules.auth.application.service import AuthResult, AuthService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest, service: FromDishka[AuthService]
) -> AuthResponse:
    result = await service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        tenant_name=body.tenant_name,
    )
    return _to_auth_response(result)


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest, service: FromDishka[AuthService]
) -> AuthResponse:
    result = await service.login(email=body.email, password=body.password)
    return _to_auth_response(result)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest, service: FromDishka[AuthService]
) -> TokenResponse:
    pair = await service.refresh(refresh_token=body.refresh_token)
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        access_expires_at=pair.access_expires_at,
        refresh_expires_at=pair.refresh_expires_at,
    )


@router.get("/me", response_model=UserResponse)
async def me(
    payload: Annotated[TokenPayload, Depends(current_user)],
    service: FromDishka[AuthService],
) -> UserResponse:
    from uuid import UUID

    from anasklad.core.http.errors import NotFoundError
    # service has repo via DI, but simplest: use repo directly — keep narrow for MVP
    user = await service._users.get_by_id(UUID(payload.sub))  # noqa: SLF001 (OK inside module)
    if user is None:
        raise NotFoundError("user not found")
    return _user_to_response(user)


def _to_auth_response(result: AuthResult) -> AuthResponse:
    return AuthResponse(
        user=_user_to_response(result.user),
        tokens=TokenResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
            access_expires_at=result.tokens.access_expires_at,
            refresh_expires_at=result.tokens.refresh_expires_at,
        ),
    )


def _user_to_response(u: "User") -> UserResponse:  # type: ignore[name-defined]  # noqa: F821
    return UserResponse(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        tenant_id=u.tenant_id,
        is_superuser=u.is_superuser,
        created_at=u.created_at,
    )
