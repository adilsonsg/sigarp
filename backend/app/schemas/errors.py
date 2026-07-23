from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    loc: list[str | int] = Field(default_factory=list)
    message: str
    type: str | None = None


class ErrorResponse(BaseModel):
    detail: str
    code: str
    request_id: str
    errors: list[ErrorDetail] = Field(default_factory=list)
