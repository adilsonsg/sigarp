from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.error_handlers import register_exception_handlers
from app.api.responses import UTF8JSONResponse
from app.api.routes.auth import router as auth_router
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.organizations import router as organizations_router
from app.api.routes.pncp import router as pncp_router
from app.api.routes.system import router as system_router
from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware

WEB_DIR = Path(__file__).resolve().parent / "web"


def create_app() -> FastAPI:
    configure_logging()

    application = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description=("Sistema Inteligente de Gestão e Análise de Registro de Preços"),
        default_response_class=UTF8JSONResponse,
    )

    application.add_middleware(RequestContextMiddleware)
    register_exception_handlers(application)

    application.include_router(system_router)
    application.include_router(auth_router, deprecated=True)
    application.include_router(organizations_router, deprecated=True)
    application.include_router(pncp_router, deprecated=True)
    application.include_router(opportunities_router, deprecated=True)
    application.include_router(api_v1_router)

    @application.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/consulta")

    @application.get("/consulta", include_in_schema=False)
    def consultation_page() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    application.mount(
        "/consulta/assets",
        StaticFiles(directory=WEB_DIR),
        name="consultation-assets",
    )

    return application
