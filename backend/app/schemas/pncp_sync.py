from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PNCPContractingInput(BaseModel):
    numero_controle_pncp: str = Field(min_length=3, max_length=100)
    numero_compra: str | None = None
    ano_compra: int | None = None
    processo: str | None = None
    objeto_compra: str = Field(min_length=3)
    modalidade_id: int | None = None
    modalidade_nome: str | None = None
    situacao_compra_nome: str | None = None
    srp: bool | None = None
    data_publicacao_pncp: datetime | None = None
    valor_total_estimado: Decimal | None = None
    valor_total_homologado: Decimal | None = None
    orgao_cnpj: str | None = None
    orgao_razao_social: str | None = None
    unidade_nome: str | None = None
    uf: str | None = None
    municipio: str | None = None
    link_sistema_origem: str | None = None
    dados_fonte: dict[str, Any] | None = None


class PNCPSyncStats(BaseModel):
    paginas_processadas: int = 0
    lidos: int = 0
    inseridos: int = 0
    atualizados: int = 0
    ignorados: int = 0
    erros: int = 0
