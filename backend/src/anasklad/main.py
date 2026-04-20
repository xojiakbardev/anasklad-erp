"""FastAPI app factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from anasklad.config import get_settings
from anasklad.core.http.errors import register_error_handlers
from anasklad.core.http.middleware import CorrelationIdMiddleware
from anasklad.core.observability.logging import configure_logging, log
from anasklad.di.container import build_container
from anasklad.modules.auth.api.router import router as auth_router
from anasklad.modules.catalog.api.router import router as catalog_router
from anasklad.modules.finance.api.router import router as finance_router
from anasklad.modules.integrations.api.router import router as integrations_router
from anasklad.modules.orders.api.router import router as orders_router
from anasklad.modules.reporting.api.router import router as reporting_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(level=settings.log_level, json_output=settings.is_prod)
    settings.assert_production_ready()

    container = build_container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        log.info("startup.begin", env=settings.app_env)

        engine = await container.get(AsyncEngine)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        log.info("startup.postgres.ok")

        redis = await container.get(Redis)
        if not await redis.ping():
            raise RuntimeError("redis ping failed")
        log.info("startup.redis.ok")

        log.info("startup.ready")
        yield
        log.info("shutdown.begin")
        await container.close()
        log.info("shutdown.done")

    app = FastAPI(
        title="Anasklad-ERP API",
        version="0.1.0",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    @app.get("/health/live", tags=["health"])
    async def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def health_ready() -> dict[str, str]:
        engine = await container.get(AsyncEngine)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        redis = await container.get(Redis)
        await redis.ping()
        return {"status": "ready"}

    app.include_router(auth_router, prefix="/api")
    app.include_router(integrations_router, prefix="/api")
    app.include_router(catalog_router, prefix="/api")
    app.include_router(orders_router, prefix="/api")
    app.include_router(finance_router, prefix="/api")
    app.include_router(reporting_router, prefix="/api")

    setup_dishka(container, app)
    return app


app = create_app()
