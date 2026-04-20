"""JWT access + refresh token issuing and verification."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt

TokenType = Literal["access", "refresh"]


@dataclass(slots=True, frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


@dataclass(slots=True, frozen=True)
class TokenPayload:
    sub: str  # user id
    jti: str
    type: TokenType
    exp: datetime
    iat: datetime
    tenant_id: str | None = None


class JwtService:
    def __init__(
        self,
        *,
        secret: str,
        algorithm: str = "HS256",
        access_ttl_minutes: int = 30,
        refresh_ttl_days: int = 30,
        issuer: str = "anasklad",
    ) -> None:
        self._secret = secret
        self._alg = algorithm
        self._access_ttl = timedelta(minutes=access_ttl_minutes)
        self._refresh_ttl = timedelta(days=refresh_ttl_days)
        self._iss = issuer

    def issue_pair(self, user_id: str, *, tenant_id: str | None = None) -> TokenPair:
        now = datetime.now(UTC)
        access = self._make_token(user_id, "access", now + self._access_ttl, now, tenant_id)
        refresh = self._make_token(user_id, "refresh", now + self._refresh_ttl, now, tenant_id)
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            access_expires_at=now + self._access_ttl,
            refresh_expires_at=now + self._refresh_ttl,
        )

    def verify(self, token: str, *, expected_type: TokenType = "access") -> TokenPayload:
        try:
            decoded = jwt.decode(
                token, self._secret, algorithms=[self._alg], issuer=self._iss
            )
        except jwt.ExpiredSignatureError as e:
            raise _expired() from e
        except jwt.InvalidTokenError as e:
            raise _invalid() from e

        if decoded.get("type") != expected_type:
            raise _invalid()

        return TokenPayload(
            sub=decoded["sub"],
            jti=decoded["jti"],
            type=decoded["type"],
            exp=datetime.fromtimestamp(decoded["exp"], tz=UTC),
            iat=datetime.fromtimestamp(decoded["iat"], tz=UTC),
            tenant_id=decoded.get("tenant_id"),
        )

    def _make_token(
        self,
        user_id: str,
        token_type: TokenType,
        exp: datetime,
        iat: datetime,
        tenant_id: str | None,
    ) -> str:
        payload: dict[str, Any] = {
            "sub": user_id,
            "jti": uuid.uuid4().hex,
            "iss": self._iss,
            "type": token_type,
            "iat": int(iat.timestamp()),
            "exp": int(exp.timestamp()),
        }
        if tenant_id:
            payload["tenant_id"] = tenant_id
        return jwt.encode(payload, self._secret, algorithm=self._alg)


def _expired() -> Exception:
    from anasklad.core.http.errors import AuthError

    return AuthError("token expired", code="auth.token_expired", status=401)


def _invalid() -> Exception:
    from anasklad.core.http.errors import AuthError

    return AuthError("invalid token", code="auth.token_invalid", status=401)
