"""Shop (Organization) DTO — /v1/shops."""
from __future__ import annotations

from pydantic import Field

from uzum_connector.models.common import _Base


class Shop(_Base):
    id: int
    name: str | None = None

    # Uzum returns `OrganizationDto`; only id+name are documented.
    # Extra fields are tolerated by _Base.extra="ignore".

    def __str__(self) -> str:  # pragma: no cover
        return f"Shop(id={self.id}, name={self.name!r})"
