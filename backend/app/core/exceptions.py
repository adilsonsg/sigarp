from fastapi import status


class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


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
