from fastapi import status


class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.headers = headers or {}


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Recurso não encontrado.") -> None:
        super().__init__(
            message=message,
            code="resource_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Conflito de dados.") -> None:
        super().__init__(
            message=message,
            code="resource_conflict",
            status_code=status.HTTP_409_CONFLICT,
        )


class AuthenticationRequiredError(AppError):
    def __init__(self, message: str = "Autenticação obrigatória.") -> None:
        super().__init__(
            message=message,
            code="authentication_required",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AccessDeniedError(AppError):
    def __init__(self, message: str = "Permissão insuficiente.") -> None:
        super().__init__(
            message=message,
            code="access_denied",
            status_code=status.HTTP_403_FORBIDDEN,
        )
