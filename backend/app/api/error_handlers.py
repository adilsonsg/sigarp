import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.collectors.exceptions import (
    RemoteAPIError,
    RemoteAPIRateLimitError,
    RemoteAPITimeoutError,
)
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))


def _error_content(
    request: Request,
    *,
    detail: str,
    code: str,
    errors: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "detail": detail,
        "code": code,
        "request_id": _request_id(request),
        "errors": errors or [],
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exception: AppError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content=_error_content(
                request,
                detail=exception.message,
                code=exception.code,
            ),
            headers=exception.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exception: RequestValidationError,
    ) -> JSONResponse:
        errors = [
            {
                "loc": list(error.get("loc", [])),
                "message": str(error.get("msg", "Valor inválido.")),
                "type": str(error.get("type", "validation_error")),
            }
            for error in exception.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_content(
                request,
                detail="Dados de entrada inválidos.",
                code="validation_error",
                errors=errors,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request,
        exception: StarletteHTTPException,
    ) -> JSONResponse:
        code_by_status = {
            status.HTTP_404_NOT_FOUND: "not_found",
            status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
        }
        return JSONResponse(
            status_code=exception.status_code,
            content=_error_content(
                request,
                detail=str(exception.detail),
                code=code_by_status.get(exception.status_code, "http_error"),
            ),
            headers=exception.headers,
        )

    @app.exception_handler(RemoteAPIRateLimitError)
    async def handle_remote_rate_limit(
        request: Request,
        exception: RemoteAPIRateLimitError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_content(
                request,
                detail=str(exception),
                code="pncp_rate_limit",
            ),
            headers={"Retry-After": "60"},
        )

    @app.exception_handler(RemoteAPITimeoutError)
    async def handle_remote_timeout(
        request: Request,
        exception: RemoteAPITimeoutError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content=_error_content(
                request,
                detail=str(exception),
                code="pncp_timeout",
            ),
        )

    @app.exception_handler(RemoteAPIError)
    async def handle_remote_api_error(
        request: Request,
        exception: RemoteAPIError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=_error_content(
                request,
                detail=str(exception),
                code="pncp_remote_error",
            ),
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
            content=_error_content(
                request,
                detail="Ocorreu um erro interno.",
                code="internal_server_error",
            ),
        )
