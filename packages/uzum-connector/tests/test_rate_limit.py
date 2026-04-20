import asyncio
import time

import pytest

from uzum_connector.rate_limit import (
    AdaptiveRateAdjuster,
    InMemoryTokenBucket,
)


async def test_bucket_allows_burst_immediately():
    b = InMemoryTokenBucket(rate=10, burst=5)
    start = time.monotonic()
    for _ in range(5):
        await b.acquire()
    elapsed = time.monotonic() - start
    assert elapsed < 0.05  # all should fit in burst


async def test_bucket_blocks_when_empty():
    b = InMemoryTokenBucket(rate=10, burst=2)
    await b.acquire()
    await b.acquire()
    start = time.monotonic()
    await b.acquire()  # should wait ~0.1s (1 token / 10 rate)
    elapsed = time.monotonic() - start
    assert 0.05 < elapsed < 0.25


async def test_bucket_rejects_overlarge_request():
    b = InMemoryTokenBucket(rate=10, burst=5)
    with pytest.raises(ValueError):
        await b.acquire(10)


def test_adjuster_decreases_on_429():
    b = InMemoryTokenBucket(rate=10, burst=10)
    a = AdaptiveRateAdjuster(b, min_rate=1, max_rate=20, decrease_factor=0.5)
    a.record_429()
    assert a.current_rate == 5


def test_adjuster_respects_min_rate():
    b = InMemoryTokenBucket(rate=2, burst=5)
    a = AdaptiveRateAdjuster(b, min_rate=1.5, decrease_factor=0.1)
    a.record_429()
    assert a.current_rate == 1.5


def test_adjuster_increases_after_streak():
    b = InMemoryTokenBucket(rate=10, burst=10)
    a = AdaptiveRateAdjuster(
        b, success_streak_for_increase=3, increase_factor=1.5, max_rate=100
    )
    a.record_success()
    a.record_success()
    assert a.current_rate == 10  # not yet
    a.record_success()
    assert a.current_rate == 15
