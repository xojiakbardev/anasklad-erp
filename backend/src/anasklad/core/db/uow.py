"""Unit of Work — one transaction per use-case."""
from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """
    Thin wrapper that makes transaction boundaries explicit.

    Usage:
        async with uow:
            await repo.add(entity)
            await uow.commit()
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._committed = False

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc is not None:
            await self.rollback()
        elif not self._committed:
            # Auto-rollback if caller forgot to commit — safer than silent commit.
            await self.rollback()

    async def commit(self) -> None:
        await self._session.commit()
        self._committed = True

    async def rollback(self) -> None:
        await self._session.rollback()
