"""Assemble the DI container from core + per-module providers."""
from __future__ import annotations

from dishka import AsyncContainer, make_async_container

from anasklad.di.core_providers import CoreProvider, DbRequestProvider
from anasklad.modules.auth.provider import AuthProvider
from anasklad.modules.catalog.provider import CatalogProvider
from anasklad.modules.integrations.provider import IntegrationsProvider
from anasklad.modules.orders.provider import OrdersProvider


def build_container() -> AsyncContainer:
    return make_async_container(
        CoreProvider(),
        DbRequestProvider(),
        AuthProvider(),
        IntegrationsProvider(),
        CatalogProvider(),
        OrdersProvider(),
    )
