from fastapi.responses import JSONResponse

from app.schemas.errors import ErrorResponse


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


COMMON_ERROR_RESPONSES: dict[int | str, dict[str, object]] = {
    401: {
        "model": ErrorResponse,
        "description": "Credenciais ausentes ou inválidas.",
    },
    403: {
        "model": ErrorResponse,
        "description": "Identidade sem permissão para a operação.",
    },
    404: {
        "model": ErrorResponse,
        "description": "Recurso não encontrado.",
    },
    409: {
        "model": ErrorResponse,
        "description": "Conflito com o estado atual do recurso.",
    },
    422: {
        "model": ErrorResponse,
        "description": "Dados de entrada inválidos.",
    },
    500: {
        "model": ErrorResponse,
        "description": "Erro interno não esperado.",
    },
}
