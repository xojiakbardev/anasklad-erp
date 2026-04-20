"""
Arq worker — scheduled & on-demand sync jobs.

Usage (dev):
    arq anasklad.modules.sync.worker.WorkerSettings
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from arq.connections import RedisSettings
from arq.cron import cron
from dishka import AsyncContainer, Scope

from anasklad.config import Settings, get_settings
from anasklad.core.observability.logging import configure_logging, log
from anasklad.di.container import build_container
from anasklad.modules.catalog.application.sync_uzum import CatalogSyncService
from anasklad.modules.integrations.domain.entities import IntegrationStatus
from anasklad.modules.integrations.infrastructure.models import IntegrationModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

logger = logging.getLogger("anasklad.sync")


async def sync_catalog_for_integration(
    ctx: dict[str, Any], integration_id: str, tenant_id: str
) -> dict[str, Any]:
    """On-demand: sync one integration's catalog."""
    container: AsyncContainer = ctx["container"]
    async with container(scope=Scope.REQUEST) as req:
        service = await req.get(CatalogSyncService)
        result = await service.sync_integration(
            integration_id=uuid.UUID(integration_id),
            tenant_id=uuid.UUID(tenant_id),
        )
    log.info(
        "sync.catalog.done",
        integration_id=integration_id,
        products=result.products_upserted,
        variants=result.variants_upserted,
    )
    return {
        "integration_id": str(result.integration_id),
        "products_upserted": result.products_upserted,
        "variants_upserted": result.variants_upserted,
    }


async def sync_catalog_cron(ctx: dict[str, Any]) -> None:
    """Scheduled: sync catalog for every active integration."""
    container: AsyncContainer = ctx["container"]
    async with container(scope=Scope.REQUEST) as req:
        session_factory: async_sessionmaker[AsyncSession] = await req.get(
            async_sessionmaker[AsyncSession]  # type: ignore[type-abstract]
        )
        async with session_factory() as session:
            stmt = select(IntegrationModel.id, IntegrationModel.tenant_id).where(
                IntegrationModel.status == IntegrationStatus.ACTIVE.value
            )
            rows = (await session.execute(stmt)).all()

    log.info("sync.catalog.cron.started", integrations=len(rows))

    for integration_id, tenant_id in rows:
        # Schedule per-integration job — non-blocking, isolated failure.
        await ctx["redis"].enqueue_job(
            "sync_catalog_for_integration",
            str(integration_id),
            str(tenant_id),
            _job_id=f"sync_catalog:{integration_id}",
        )


async def on_startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    configure_logging(level=settings.log_level, json_output=settings.is_prod)
    ctx["container"] = build_container()
    ctx["settings"] = settings
    log.info("worker.startup", env=settings.app_env)


async def on_shutdown(ctx: dict[str, Any]) -> None:
    container: AsyncContainer = ctx["container"]
    await container.close()
    log.info("worker.shutdown")


def _redis_settings() -> RedisSettings:
    s: Settings = get_settings()
    # Parse redis://host:port/db
    url = s.redis_url.replace("redis://", "")
    host, rest = url.split(":", 1)
    port_db = rest.split("/", 1)
    port = int(port_db[0])
    database = int(port_db[1]) if len(port_db) > 1 else 0
    return RedisSettings(host=host, port=port, database=database)


class WorkerSettings:
    """Entry point for `arq`."""

    functions = [sync_catalog_for_integration]
    cron_jobs = [
        cron(sync_catalog_cron, minute={0, 30}),  # every 30 minutes
    ]
    on_startup = on_startup
    on_shutdown = on_shutdown
    redis_settings = _redis_settings()
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
