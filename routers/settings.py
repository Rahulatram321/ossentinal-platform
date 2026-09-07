from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from core.security import is_authenticated, validate_csrf_token
router = APIRouter()

@router.post("/settings")
def save_settings(request: Request, slack_webhook: str = Form(""), email: str = Form(""), csrf_token: str = Form("")):
    if not is_authenticated(request): return RedirectResponse("/login", 303)
    if not validate_csrf_token(request.session, csrf_token): return RedirectResponse("/settings?error=csrf", 303)
    return RedirectResponse("/settings", 303)

@router.post("/settings/validate")
def validate_settings(request: Request, policy: str = Form(""), csrf_token: str = Form("")):
    if not is_authenticated(request) or not validate_csrf_token(request.session, csrf_token): return {"valid": False, "warnings": ["Authentication or CSRF validation failed"]}
    return {"valid": True, "warnings": []}
