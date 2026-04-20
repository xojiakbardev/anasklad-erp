"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class RegisterRequest(_Base):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=128)
    tenant_name: str = Field(min_length=1, max_length=128)


class LoginRequest(_Base):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(_Base):
    refresh_token: str


class UserResponse(_Base):
    id: UUID
    email: str
    full_name: str | None
    tenant_id: UUID
    is_superuser: bool
    created_at: datetime


class TokenResponse(_Base):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    access_expires_at: datetime
    refresh_expires_at: datetime


class AuthResponse(_Base):
    user: UserResponse
    tokens: TokenResponse
