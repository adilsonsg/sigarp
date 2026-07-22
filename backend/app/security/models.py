from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class AccessRole(StrEnum):
    LEITOR = "leitor"
    ANALISTA = "analista"
    ADMINISTRADOR = "administrador"

    @property
    def level(self) -> int:
        return {
            AccessRole.LEITOR: 10,
            AccessRole.ANALISTA: 20,
            AccessRole.ADMINISTRADOR: 30,
        }[self]


class AuthPrincipalConfig(BaseModel):
    subject: str = Field(min_length=2, max_length=150)
    name: str = Field(min_length=2, max_length=200)
    role: AccessRole | None = None
    token_sha256: str = Field(min_length=64, max_length=64)

    @field_validator("token_sha256")
    @classmethod
    def validate_token_hash(cls, value: str) -> str:
        normalized = value.lower()
        if any(character not in "0123456789abcdef" for character in normalized):
            raise ValueError("token_sha256 deve ser hexadecimal com 64 caracteres")
        return normalized


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    subject: str
    name: str
    role: AccessRole | None
