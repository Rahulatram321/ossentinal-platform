"""Shared FastAPI dependencies; handlers should not reach into globals."""
from collections.abc import Generator
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from core.database import SessionLocal
from app.core.security import is_authenticated


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_authenticated_user(request: Request) -> str:
    if not is_authenticated(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return request.session.get("github_id", "demo")


CurrentUser = Depends(require_authenticated_user)
