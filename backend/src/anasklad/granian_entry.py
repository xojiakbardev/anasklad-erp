"""Granian launcher. Run with: python -m anasklad.granian_entry"""
from __future__ import annotations

from granian.constants import Interfaces
from granian.server import Server

from anasklad.config import get_settings


def main() -> None:
    settings = get_settings()
    server = Server(
        target="anasklad.main:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        workers=1 if not settings.is_prod else 2,
        loop="rloop",
        http="auto",
        log_enabled=True,
        log_level=settings.log_level.lower(),
    )
    server.serve()


if __name__ == "__main__":
    main()
