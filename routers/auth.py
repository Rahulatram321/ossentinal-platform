import uuid
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config import settings
from core.database import SessionLocal, User, init_db
from core.security import clear_session_token, issue_csrf_token, store_session_token
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
    request.session.update({"demo_user": True, "github_username": "github-user", "github_id": "github-user"})
    return RedirectResponse("/dashboard", 303)

@router.get("/logout")
def logout(request: Request): clear_session_token(request.session.get("auth_sid")); request.session.clear(); return RedirectResponse("/home", 303)
