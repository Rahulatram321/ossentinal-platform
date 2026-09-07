"""Compatibility location for API dependency imports."""
from app.dependencies import get_db_session, require_authenticated_user

__all__ = ["get_db_session", "require_authenticated_user"]
