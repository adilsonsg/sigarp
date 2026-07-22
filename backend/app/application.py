from fastapi import FastAPI

from app.api.error_handlers import register_exception_handlers
from app.api.responses import UTF8JSONResponse
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.organizations import router as organizations_router
from app.api.routes.pncp import router as pncp_router
from app.api.routes.system import router as system_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware


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
    application.include_router(organizations_router)
    application.include_router(pncp_router)
    application.include_router(opportunities_router)

    return application
