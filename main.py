from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import settings
from core.database import init_db, seed_demo_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_demo_data()
    yield

app = FastAPI(title=settings.app_name, version="2.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, max_age=604800, https_only=settings.session_https_only, same_site=settings.session_samesite)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
if settings.app_env == "production": app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    # Keep browser users on a branded recovery path; API callers get JSON.
    if request.url.path.startswith("/api/"):
        return HTMLResponse('{"detail":"internal server error"}', status_code=500, media_type="application/json")
    return templates.TemplateResponse(request, "error.html", {"error": "An unexpected error occurred."}, status_code=500)

@app.get("/health")
def health():
    return {"status": "ok", "version": app.version, "modules": {"triage": settings.feature_triage, "prism": settings.feature_prism, "gitpulse": settings.feature_gitpulse}, "env": settings.app_env}

@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/home")

from routers import public, auth, app as app_router, api, webhook_router, settings as settings_router
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(app_router.router)
app.include_router(api.router)
app.include_router(webhook_router.router)
app.include_router(settings_router.router)
