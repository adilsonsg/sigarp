import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.collectors.exceptions import (
    RemoteAPIError,
    RemoteAPIRateLimitError,
    RemoteAPITimeoutError,
)
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exception: AppError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "detail": exception.message,
                "code": exception.code,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(RemoteAPIRateLimitError)
    async def handle_remote_rate_limit(
        request: Request,
        exception: RemoteAPIRateLimitError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": str(exception),
                "code": "pncp_rate_limit",
                "request_id": getattr(request.state, "request_id", None),
            },
            headers={"Retry-After": "60"},
        )

    @app.exception_handler(RemoteAPITimeoutError)
    async def handle_remote_timeout(
        request: Request,
        exception: RemoteAPITimeoutError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "detail": str(exception),
                "code": "pncp_timeout",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(RemoteAPIError)
    async def handle_remote_api_error(
        request: Request,
        exception: RemoteAPIError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "detail": str(exception),
                "code": "pncp_remote_error",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exception: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Erro inesperado",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Ocorreu um erro interno.",
                "code": "internal_server_error",
                "request_id": getattr(request.state, "request_id", None),
            },
        )
