"""Pure domain entities — no ORM, no I/O."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    password_hash: str
    full_name: str | None
    tenant_id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login_at: datetime | None = None
