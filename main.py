"""Backward-compatible ASGI entry point.

Deployments should use ``app.main:app``. This module keeps existing local and
Render commands working while the production package is introduced.
"""
from app.main import app, create_app

__all__ = ["app", "create_app"]
