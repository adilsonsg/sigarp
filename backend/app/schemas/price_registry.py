from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _digits_only(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = "".join(character for character in value if character.isdigit())
    return normalized or None


class SupplierInput(BaseModel):
    cnpj: str | None = None
    razao_social: str = Field(min_length=2, max_length=255)
    nome_fantasia: str | None = Field(default=None, max_length=255)

    @field_validator("cnpj")
    @classmethod
    def normalize_cnpj(cls, value: str | None) -> str | None:
        normalized = _digits_only(value)
        if normalized is not None and len(normalized) != 14:
            raise ValueError("O CNPJ deve conter 14 dígitos.")
        return normalized


class PriceRegistryItemInput(BaseModel):
    numero_item: int = Field(ge=1)
    descricao: str = Field(min_length=2)
    fabricante: str | None = Field(default=None, max_length=255)
    marca: str | None = Field(default=None, max_length=255)
    modelo: str | None = Field(default=None, max_length=255)
    unidade_medida: str | None = Field(default=None, max_length=50)
    quantidade_registrada: Decimal | None = Field(default=None, ge=0)
    quantidade_empenhada: Decimal | None = Field(default=None, ge=0)
    saldo_estimado: Decimal | None = Field(default=None, ge=0)
    limite_adesao: Decimal | None = Field(default=None, ge=0)
    valor_unitario: Decimal | None = Field(default=None, ge=0)
    fornecedor: SupplierInput | None = None
    dados_fonte: dict[str, Any] | None = None


class PriceRegistryRecordInput(BaseModel):
    numero_controle_pncp: str = Field(min_length=3, max_length=100)
    numero_ata: str | None = Field(default=None, max_length=100)
    numero_processo: str | None = Field(default=None, max_length=100)
    objeto: str = Field(min_length=3)
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    situacao: str | None = Field(default=None, max_length=50)
    orgao_gerenciador_id: int = Field(gt=0)
    url_pncp: str | None = Field(default=None, max_length=500)
    dados_fonte: dict[str, Any] | None = None
    itens: list[PriceRegistryItemInput] = Field(default_factory=list)

    @field_validator("vigencia_fim")
    @classmethod
    def validate_end_date(cls, value: date | None, info):  # type: ignore[no-untyped-def]
        start_date = info.data.get("vigencia_inicio")
        if value is not None and start_date is not None and value < start_date:
            raise ValueError("A vigência final não pode ser anterior à inicial.")
        return value


class PriceRegistryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_item: int
    descricao: str
    fabricante: str | None
    marca: str | None
    modelo: str | None
    unidade_medida: str | None
    quantidade_registrada: Decimal | None
    quantidade_empenhada: Decimal | None
    saldo_estimado: Decimal | None
    limite_adesao: Decimal | None
    valor_unitario: Decimal | None


class PriceRegistryRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_controle_pncp: str
    numero_ata: str | None
    numero_processo: str | None
    objeto: str
    vigencia_inicio: date | None
    vigencia_fim: date | None
    situacao: str | None
    orgao_gerenciador_id: int
    url_pncp: str | None
    itens: list[PriceRegistryItemRead]
