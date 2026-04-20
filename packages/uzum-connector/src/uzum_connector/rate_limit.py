"""Token-bucket rate limiters (in-memory and Redis-backed)."""
from __future__ import annotations

import asyncio
import time
from typing import Protocol


class RateLimiter(Protocol):
    """Any object that can gate requests."""

    async def acquire(self, tokens: int = 1) -> None: ...


class InMemoryTokenBucket:
    """
    Classic token bucket. Process-local.

    - `rate` tokens replenish per second.
    - `burst` is the maximum bucket size.
    - `acquire(n)` blocks until n tokens are available.

    Thread-safe for asyncio (asyncio.Lock), NOT for multi-process use.
    """

    __slots__ = ("_rate", "_burst", "_tokens", "_updated_at", "_lock")

    def __init__(self, rate: float, burst: int) -> None:
        if rate <= 0:
            raise ValueError("rate must be > 0")
        if burst <= 0:
            raise ValueError("burst must be > 0")
        self._rate = float(rate)
        self._burst = int(burst)
        self._tokens = float(burst)
        self._updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        if tokens > self._burst:
            raise ValueError(f"requested {tokens} tokens exceeds burst {self._burst}")

        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                # Not enough tokens — compute sleep time outside the lock.
                deficit = tokens - self._tokens
                sleep_for = deficit / self._rate
            await asyncio.sleep(sleep_for)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._updated_at
        if elapsed > 0:
            self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
            self._updated_at = now


class NoopRateLimiter:
    """Passthrough limiter, useful for tests."""

    async def acquire(self, tokens: int = 1) -> None:  # noqa: ARG002
        return None


class AdaptiveRateAdjuster:
    """
    Tracks 429 vs success responses and nudges a bucket's rate up/down.

    Wrap an InMemoryTokenBucket: call `record_success()` or `record_429()`
    after each request. Read `.current_rate` for observability.
    """

    def __init__(
        self,
        bucket: InMemoryTokenBucket,
        *,
        min_rate: float = 0.5,
        max_rate: float = 20.0,
        success_streak_for_increase: int = 100,
        increase_factor: float = 1.1,
        decrease_factor: float = 0.5,
    ) -> None:
        self._bucket = bucket
        self._min_rate = min_rate
        self._max_rate = max_rate
        self._streak = success_streak_for_increase
        self._inc = increase_factor
        self._dec = decrease_factor
        self._consecutive_successes = 0

    @property
    def current_rate(self) -> float:
        return self._bucket._rate  # type: ignore[attr-defined]

    def record_success(self) -> None:
        self._consecutive_successes += 1
        if self._consecutive_successes >= self._streak:
            self._consecutive_successes = 0
            new_rate = min(self._max_rate, self._bucket._rate * self._inc)  # type: ignore[attr-defined]
            self._bucket._rate = new_rate  # type: ignore[attr-defined]

    def record_429(self) -> None:
        self._consecutive_successes = 0
        new_rate = max(self._min_rate, self._bucket._rate * self._dec)  # type: ignore[attr-defined]
        self._bucket._rate = new_rate  # type: ignore[attr-defined]
