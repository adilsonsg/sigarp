from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Sphere = Literal["federal", "estadual", "municipal", "distrital"]


class OrganizationBase(BaseModel):
    nome: str = Field(min_length=3, max_length=255)
    sigla: str | None = Field(default=None, max_length=50)
    cnpj: str | None = Field(default=None)
    esfera: Sphere
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    municipio: str | None = Field(default=None, max_length=100)

    @field_validator("nome", "sigla", "municipio", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @field_validator("sigla")
    @classmethod
    def normalize_sigla(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @field_validator("uf")
    @classmethod
    def normalize_uf(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value: str | None) -> str | None:
        if value is None:
            return value

        digits = "".join(character for character in value if character.isdigit())
        if len(digits) != 14:
            raise ValueError("O CNPJ deve conter 14 dígitos.")
        return digits


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: int
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
