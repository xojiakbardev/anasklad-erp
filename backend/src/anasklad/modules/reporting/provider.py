"""Dishka provider for reporting module."""
from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from anasklad.modules.reporting.application.service import ReportingService


class ReportingProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def service(self, session: AsyncSession) -> ReportingService:
        return ReportingService(session)
