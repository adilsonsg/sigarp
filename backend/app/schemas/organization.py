from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Sphere = Literal["federal", "estadual", "municipal", "distrital"]

class OrganizationBase(BaseModel):
    nome: str = Field(min_length=3, max_length=255)
    sigla: str | None = Field(default=None, max_length=50)
    cnpj: str | None = None
    esfera: Sphere
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    municipio: str | None = Field(default=None, max_length=100)

    @field_validator("nome", "sigla", "municipio", mode="before")
    @classmethod
    def strip_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("sigla")
    @classmethod
    def normalize_sigla(cls, value):
        return value.upper() if value else value

    @field_validator("uf")
    @classmethod
    def normalize_uf(cls, value):
        return value.upper() if value else value

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value):
        if value is None:
            return value
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 14:
            raise ValueError("O CNPJ deve conter 14 dígitos.")
        return digits

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    criado_em: datetime
    model_config = ConfigDict(from_attributes=True)
