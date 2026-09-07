import uuid
from datetime import datetime
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config import settings
from core.database import SessionLocal, User, init_db
from core.security import clear_session_token, issue_csrf_token, store_session_token, validate_csrf_token
router = APIRouter(); templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login(request: Request): return templates.TemplateResponse(request, "auth/login.html", {"csrf_token": issue_csrf_token(request.session)})

@router.get("/demo")
def demo(request: Request):
    if settings.allow_demo_login: request.session.update({"demo_user": True, "github_username": "demo-maintainer", "github_id": "demo"})
    return RedirectResponse("/dashboard", 303)

@router.get("/auth/github")
def github_auth(request: Request):
    if not settings.github_client_id: return RedirectResponse("/demo", 303)
    state = issue_csrf_token(request.session)
    return RedirectResponse(f"https://github.com/login/oauth/authorize?client_id={settings.github_client_id}&scope={settings.github_oauth_scope}&state={state}")

@router.get("/auth/callback")
def callback(request: Request, code: str = "", state: str = ""):
    if not code or not validate_csrf_token(request.session, state):
        return RedirectResponse("/login?error=invalid_oauth_state", 303)
    request.session.pop("csrf_token", None)
    try:
        token_response = httpx.post("https://github.com/login/oauth/access_token", headers={"Accept": "application/json"}, json={
            "client_id": settings.github_client_id, "client_secret": settings.github_client_secret, "code": code,
        }, timeout=10)
        token = token_response.json().get("access_token", "")
        if not token:
            raise ValueError("GitHub did not return an access token")
        profile = httpx.get("https://api.github.com/user", headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}, timeout=10).json()
        github_id, username = str(profile["id"]), profile["login"]
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(github_id=github_id).one_or_none()
            if user is None:
                user = User(github_id=github_id, username=username, avatar_url=profile.get("avatar_url", ""), email=profile.get("email") or "")
                db.add(user)
            else:
                user.username, user.last_login_at = username, datetime.utcnow()
            db.commit()
        finally:
            db.close()
        sid = uuid.uuid4().hex
        store_session_token(sid, token)
        request.session.update({"auth_sid": sid, "github_username": username, "github_id": github_id})
    except (httpx.HTTPError, KeyError, ValueError):
        return RedirectResponse("/login?error=github_auth_failed", 303)
    return RedirectResponse("/dashboard", 303)

@router.get("/logout")
def logout(request: Request): clear_session_token(request.session.get("auth_sid")); request.session.clear(); return RedirectResponse("/home", 303)
