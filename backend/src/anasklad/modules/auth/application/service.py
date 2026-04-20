"""Auth use-cases — register, login, refresh."""
from __future__ import annotations

from dataclasses import dataclass

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.http.errors import AuthError, ValidationError
from anasklad.core.security.hashing import hash_password, verify_password
from anasklad.core.security.jwt import JwtService, TokenPair
from anasklad.modules.auth.domain.entities import User
from anasklad.modules.auth.infrastructure.repository import UserRepository


@dataclass(slots=True, frozen=True)
class AuthResult:
    user: User
    tokens: TokenPair


class AuthService:
    def __init__(
        self,
        uow: UnitOfWork,
        users: UserRepository,
        jwt: JwtService,
    ) -> None:
        self._uow = uow
        self._users = users
        self._jwt = jwt

    async def register(
        self, *, email: str, password: str, full_name: str | None, tenant_name: str
    ) -> AuthResult:
        if len(password) < 8:
            raise ValidationError("password must be at least 8 characters")

        async with self._uow:
            existing = await self._users.get_by_email(email)
            if existing is not None:
                raise ValidationError("email already registered", code="auth.email_taken")

            tenant_id = await self._users.create_tenant(tenant_name)
            user = await self._users.add(
                email=email,
                password_hash=hash_password(password),
                full_name=full_name,
                tenant_id=tenant_id,
            )
            tokens = self._jwt.issue_pair(str(user.id), tenant_id=str(user.tenant_id))
            await self._uow.commit()
            return AuthResult(user=user, tokens=tokens)

    async def login(self, *, email: str, password: str) -> AuthResult:
        async with self._uow:
            user = await self._users.get_by_email(email)
            if user is None or not verify_password(password, user.password_hash):
                raise AuthError("invalid email or password", code="auth.invalid_credentials")
            if not user.is_active:
                raise AuthError("account is disabled", code="auth.disabled", status=403)

            await self._users.touch_last_login(user.id)
            tokens = self._jwt.issue_pair(str(user.id), tenant_id=str(user.tenant_id))
            await self._uow.commit()
            return AuthResult(user=user, tokens=tokens)

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        payload = self._jwt.verify(refresh_token, expected_type="refresh")
        return self._jwt.issue_pair(payload.sub, tenant_id=payload.tenant_id)
