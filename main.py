from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import settings
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.app_name, version="2.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, max_age=604800, https_only=settings.session_https_only, same_site=settings.session_samesite)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
if settings.app_env == "production": app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
