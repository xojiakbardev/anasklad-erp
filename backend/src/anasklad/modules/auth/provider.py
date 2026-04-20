"""Dishka provider for the auth module."""
from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.core.db.uow import UnitOfWork
from anasklad.core.security.jwt import JwtService
from anasklad.modules.auth.application.service import AuthService
from anasklad.modules.auth.infrastructure.repository import UserRepository


class AuthProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide
    def auth_service(
        self, uow: UnitOfWork, users: UserRepository, jwt: JwtService
    ) -> AuthService:
        return AuthService(uow, users, jwt)
