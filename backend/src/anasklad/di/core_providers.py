"""Framework-level Dishka providers (settings, db, redis, security)."""
from __future__ import annotations

from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from anasklad.config import Settings, get_settings
from anasklad.core.db.session import build_engine, build_session_factory
from anasklad.core.db.uow import UnitOfWork
from anasklad.core.security.crypto import CryptoService
from anasklad.core.security.jwt import JwtService


class CoreProvider(Provider):
    scope = Scope.APP

    @provide
    def settings(self) -> Settings:
        return get_settings()

    @provide
    def engine(self, settings: Settings) -> AsyncEngine:
        return build_engine(settings.database_url)

    @provide
    def session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return build_session_factory(engine)

    @provide
    async def redis(self, settings: Settings) -> AsyncIterator[Redis]:
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        try:
            yield client
        finally:
            await client.aclose()

    @provide
    def crypto(self, settings: Settings) -> CryptoService:
        key = settings.credentials_fernet_key
        if not key:
            # Dev fallback — stable per-process but NOT persistent
            key = CryptoService.generate_key()
        return CryptoService(key)

    @provide
    def jwt_service(self, settings: Settings) -> JwtService:
        return JwtService(
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            access_ttl_minutes=settings.jwt_access_ttl_minutes,
            refresh_ttl_days=settings.jwt_refresh_ttl_days,
        )


class DbRequestProvider(Provider):
    """Request-scoped DB session + UoW."""

    scope = Scope.REQUEST

    @provide
    async def session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @provide
    def uow(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)
