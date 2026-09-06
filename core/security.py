import secrets
from typing import Any
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

_session_tokens: dict[str, str] = {}


def issue_csrf_token(session: dict[str, Any]) -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token


def validate_csrf_token(session: dict[str, Any], token: str | None) -> bool:
    expected = session.get("csrf_token", "")
    return bool(token and expected and secrets.compare_digest(expected, token))


def get_session_token(request: Request) -> str | None:
    sid = request.session.get("auth_sid")
    return _session_tokens.get(sid) if sid else None


def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("demo_user") or request.session.get("auth_sid"))


def require_auth(request: Request) -> None:
    if not is_authenticated(request):
        raise HTTPException(status_code=307, headers={"Location": "/login"})


def store_session_token(session_id: str, token: str) -> None:
    _session_tokens[session_id] = token


def clear_session_token(session_id: str | None) -> None:
    if session_id:
        _session_tokens.pop(session_id, None)
