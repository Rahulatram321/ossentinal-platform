"""Compatibility import path; canonical settings live in :mod:`app.config`."""
from app.config import Settings, settings

__all__ = ["Settings", "settings"]
