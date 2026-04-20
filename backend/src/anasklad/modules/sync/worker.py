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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from anasklad.config import Settings, get_settings
from anasklad.core.observability.logging import configure_logging, log
from anasklad.di.container import build_container
from anasklad.modules.catalog.application.sync_uzum import CatalogSyncService
from anasklad.modules.finance.application.service import FinanceService
from anasklad.modules.integrations.domain.entities import IntegrationStatus
from anasklad.modules.integrations.infrastructure.models import IntegrationModel
from anasklad.modules.orders.application.service import OrderService

logger = logging.getLogger("anasklad.sync")


async def sync_catalog_for_integration(
    ctx: dict[str, Any], integration_id: str, tenant_id: str
) -> dict[str, Any]:
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
        "products_upserted": result.products_upserted,
        "variants_upserted": result.variants_upserted,
    }


async def sync_orders_for_integration(
    ctx: dict[str, Any], integration_id: str, tenant_id: str
) -> dict[str, Any]:
    container: AsyncContainer = ctx["container"]
    async with container(scope=Scope.REQUEST) as req:
        service = await req.get(OrderService)
        result = await service.sync(
            integration_id=uuid.UUID(integration_id),
            tenant_id=uuid.UUID(tenant_id),
        )
    log.info(
        "sync.orders.done",
        integration_id=integration_id,
        orders=result.orders_upserted,
    )
    return {"orders_upserted": result.orders_upserted}


async def sync_finance_for_integration(
    ctx: dict[str, Any], integration_id: str, tenant_id: str
) -> dict[str, Any]:
    container: AsyncContainer = ctx["container"]
    async with container(scope=Scope.REQUEST) as req:
        service = await req.get(FinanceService)
        result = await service.sync(
            integration_id=uuid.UUID(integration_id),
            tenant_id=uuid.UUID(tenant_id),
            days_back=30,
        )
    log.info(
        "sync.finance.done",
        integration_id=integration_id,
        sales=result.sales_upserted,
        expenses=result.expenses_upserted,
    )
    return {
        "sales_upserted": result.sales_upserted,
        "expenses_upserted": result.expenses_upserted,
    }


async def _fanout_active_integrations(ctx: dict[str, Any], job_name: str) -> None:
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

    log.info("sync.cron.fanout", job=job_name, integrations=len(rows))
    for integration_id, tenant_id in rows:
        await ctx["redis"].enqueue_job(
            job_name,
            str(integration_id),
            str(tenant_id),
            _job_id=f"{job_name}:{integration_id}",
        )


async def sync_catalog_cron(ctx: dict[str, Any]) -> None:
    await _fanout_active_integrations(ctx, "sync_catalog_for_integration")


async def sync_orders_cron(ctx: dict[str, Any]) -> None:
    await _fanout_active_integrations(ctx, "sync_orders_for_integration")


async def sync_finance_cron(ctx: dict[str, Any]) -> None:
    await _fanout_active_integrations(ctx, "sync_finance_for_integration")


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
    url = s.redis_url.replace("redis://", "")
    host, rest = url.split(":", 1)
    port_db = rest.split("/", 1)
    port = int(port_db[0])
    database = int(port_db[1]) if len(port_db) > 1 else 0
    return RedisSettings(host=host, port=port, database=database)


class WorkerSettings:
    functions = [
        sync_catalog_for_integration,
        sync_orders_for_integration,
        sync_finance_for_integration,
    ]
    cron_jobs = [
        cron(sync_orders_cron, minute=set(range(0, 60, 2))),     # every 2 min
        cron(sync_finance_cron, minute=set(range(0, 60, 10))),   # every 10 min
        cron(sync_catalog_cron, minute={0, 30}),                 # every 30 min
    ]
    on_startup = on_startup
    on_shutdown = on_shutdown
    redis_settings = _redis_settings()
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
