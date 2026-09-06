from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
router = APIRouter(); templates = Jinja2Templates(directory="templates")

@router.get("/home")
def home(request: Request): return templates.TemplateResponse(request, "public/landing.html", {})

@router.get("/pricing")
def pricing(request: Request): return templates.TemplateResponse(request, "public/pricing.html", {})

@router.get("/docs")
def docs(): return RedirectResponse("https://github.com/ossentinel/ossentinel")
