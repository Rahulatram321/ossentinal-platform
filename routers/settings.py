from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from core.security import is_authenticated, validate_csrf_token
router = APIRouter()

@router.post("/settings")
def save_settings(request: Request, slack_webhook: str = Form(""), email: str = Form("")):
    if not is_authenticated(request): return RedirectResponse("/login", 303)
    return RedirectResponse("/settings", 303)

@router.post("/settings/validate")
def validate_settings(request: Request, policy: str = Form("")): return {"valid": True, "warnings": []}
