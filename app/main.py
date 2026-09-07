"""FastAPI application factory for production deployments."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.api.health import router as health_router
from app.api.v1.gitpulse import router as gitpulse_api_router
from app.api.v1.prism import router as prism_api_router
from app.config import settings
from app.core.exceptions import OSSentinelError
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.db.init_db import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    initialize_database(seed_demo=settings.allow_demo_login)
    yield


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version="3.0.0", lifespan=lifespan)
    application.add_middleware(RequestContextMiddleware)
    application.add_middleware(SessionMiddleware, secret_key=settings.session_secret, max_age=604800,
                               https_only=settings.session_https_only, same_site=settings.session_samesite)
    application.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                               allow_methods=["*"], allow_headers=["*"])
    if settings.app_env == "production":
        application.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
    application.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    @application.exception_handler(OSSentinelError)
    async def application_error(_: Request, error: OSSentinelError):
        return HTMLResponse(f'{{"detail":"{error.public_message}"}}', status_code=error.status_code,
                            media_type="application/json")

    @application.exception_handler(Exception)
    async def unhandled_exception(request: Request, _: Exception):
        if request.url.path.startswith("/api/"):
            return HTMLResponse('{"detail":"internal server error"}', status_code=500, media_type="application/json")
        return templates.TemplateResponse(request, "error.html", {"error": "An unexpected error occurred."}, status_code=500)

    @application.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse("/home")

    application.include_router(health_router)
    from routers import api, app as app_router, auth, public, settings as settings_router, webhook_router
    application.include_router(public.router)
    application.include_router(auth.router)
    application.include_router(app_router.router)
    application.include_router(api.router)
    application.include_router(webhook_router.router)
    application.include_router(settings_router.router)
    application.include_router(prism_api_router)
    application.include_router(gitpulse_api_router)
    return application


app = create_app()
