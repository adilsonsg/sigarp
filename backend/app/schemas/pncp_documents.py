from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PNCPContractingDocumentInput(BaseModel):
    contracting_id: int
    sequencial_documento: int = Field(ge=1)
    titulo: str | None = None
    tipo_documento_id: int | None = None
    tipo_documento_nome: str | None = None
    url: str | None = None
    uri: str | None = None
    data_publicacao_pncp: datetime | None = None
    dados_fonte: dict[str, Any] | None = None


class PNCPDocumentSyncStats(BaseModel):
    contratacoes_processadas: int = 0
    documentos_lidos: int = 0
    inseridos: int = 0
    atualizados: int = 0
    ignorados: int = 0
    erros: int = 0


class PNCPDocumentAnalysisStats(BaseModel):
    documentos_processados: int = 0
    sucessos: int = 0
    sem_texto: int = 0
    tipos_nao_suportados: int = 0
    limites_excedidos: int = 0
    ignorados: int = 0
    erros: int = 0
