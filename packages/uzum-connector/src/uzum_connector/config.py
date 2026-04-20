"""Client configuration."""
from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_BASE_URL = "https://api-seller.uzum.uz/api/seller-openapi"


@dataclass(slots=True, frozen=True)
class ClientConfig:
    """Tunables for the Uzum HTTP client."""

    token: str
    base_url: str = DEFAULT_BASE_URL

    # Timeouts (seconds)
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    write_timeout: float = 10.0
    pool_timeout: float = 5.0

    # Connection pool
    max_connections: int = 50
    max_keepalive_connections: int = 20
    http2: bool = True

    # Retry
    retry_attempts: int = 5
    retry_min_wait: float = 0.5
    retry_max_wait: float = 30.0

    # Rate limiting (per-second steady rate, burst capacity)
    rate_per_second: float = 5.0
    rate_burst: int = 10

    # Observability
    user_agent: str = field(default_factory=lambda: f"uzum-connector/0.1.0")

    def with_token(self, token: str) -> ClientConfig:
        """Return a copy with a different token (for per-tenant clients)."""
        return ClientConfig(
            token=token,
            base_url=self.base_url,
            connect_timeout=self.connect_timeout,
            read_timeout=self.read_timeout,
            write_timeout=self.write_timeout,
            pool_timeout=self.pool_timeout,
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            http2=self.http2,
            retry_attempts=self.retry_attempts,
            retry_min_wait=self.retry_min_wait,
            retry_max_wait=self.retry_max_wait,
            rate_per_second=self.rate_per_second,
            rate_burst=self.rate_burst,
            user_agent=self.user_agent,
        )
