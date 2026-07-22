from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PNCPContractingItemInput(BaseModel):
    contracting_id: int
    numero_item: int = Field(ge=1)
    descricao: str = Field(min_length=1)
    material_ou_servico: str | None = None
    material_ou_servico_nome: str | None = None
    quantidade: Decimal | None = None
    unidade_medida: str | None = None
    valor_unitario_estimado: Decimal | None = None
    valor_total: Decimal | None = None
    situacao_item_id: int | None = None
    situacao_item_nome: str | None = None
    criterio_julgamento_id: int | None = None
    criterio_julgamento_nome: str | None = None
    tem_resultado: bool | None = None
    orcamento_sigiloso: bool | None = None
    informacao_complementar: str | None = None
    catalogo_codigo_item: str | None = None
    dados_fonte: dict[str, Any] | None = None


class PNCPItemSyncStats(BaseModel):
    contratacoes_processadas: int = 0
    paginas_processadas: int = 0
    itens_lidos: int = 0
    inseridos: int = 0
    atualizados: int = 0
    ignorados: int = 0
    erros: int = 0
