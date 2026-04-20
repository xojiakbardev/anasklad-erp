"""Alembic env — wires async engine and aggregates metadata from all modules."""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from anasklad.config import get_settings
from anasklad.core.db.base import Base

# Import models so they register with Base.metadata
from anasklad.modules.auth.infrastructure import models as _auth_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject database URL from settings/env, converting asyncpg URL to sync for offline mode if needed
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata

# Schemas managed by this app (we create them before migrations run)
MANAGED_SCHEMAS = ["auth", "catalog", "stocks", "orders", "finance", "integrations", "sync", "reporting", "cost", "core"]


def include_object(obj, name, type_, reflected, compare_to):  # noqa: ARG001
    # Only manage objects in our schemas
    if type_ == "table":
        return obj.schema in MANAGED_SCHEMAS
    return True


def _create_schemas_sync(connection: Connection) -> None:
    for schema in MANAGED_SCHEMAS:
        connection.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        version_table_schema="core",
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    _create_schemas_sync(connection)
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        include_object=include_object,
        version_table_schema="core",
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
