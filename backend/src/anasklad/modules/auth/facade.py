"""Public facade of the auth module — other modules may only import this."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from anasklad.modules.auth.infrastructure.repository import UserRepository


@dataclass(slots=True, frozen=True)
class UserRef:
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str


class AuthFacade:
    """Read-only view exposed to other modules."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def get_user(self, user_id: uuid.UUID) -> UserRef | None:
        u = await self._users.get_by_id(user_id)
        if u is None:
            return None
        return UserRef(id=u.id, tenant_id=u.tenant_id, email=u.email)
