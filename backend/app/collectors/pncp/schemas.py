from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PNCPModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class PNCPOrganization(PNCPModel):
    cnpj: str | None = None
    razao_social: str | None = Field(default=None, alias="razaoSocial")
    poder_id: str | None = Field(default=None, alias="poderId")
    esfera_id: str | None = Field(default=None, alias="esferaId")


class PNCPUnit(PNCPModel):
    codigo_unidade: str | None = Field(default=None, alias="codigoUnidade")
    nome_unidade: str | None = Field(default=None, alias="nomeUnidade")
    municipio_nome: str | None = Field(default=None, alias="municipioNome")
    uf_sigla: str | None = Field(default=None, alias="ufSigla")
    uf_nome: str | None = Field(default=None, alias="ufNome")


class PNCPModality(PNCPModel):
    id: int | None = None
    nome: str | None = None


class PNCPContracting(PNCPModel):
    numero_controle_pncp: str | None = Field(default=None, alias="numeroControlePNCP")
    numero_compra: str | None = Field(default=None, alias="numeroCompra")
    ano_compra: int | None = Field(default=None, alias="anoCompra")
    sequencial_compra: int | None = Field(default=None, alias="sequencialCompra")
    processo: str | None = None
    objeto_compra: str | None = Field(default=None, alias="objetoCompra")
    informacao_complementar: str | None = Field(
        default=None, alias="informacaoComplementar"
    )
    modalidade_id: int | None = Field(default=None, alias="modalidadeId")
    modalidade_nome: str | None = Field(default=None, alias="modalidadeNome")
    modo_disputa_id: int | None = Field(default=None, alias="modoDisputaId")
    modo_disputa_nome: str | None = Field(default=None, alias="modoDisputaNome")
    situacao_compra_id: int | None = Field(default=None, alias="situacaoCompraId")
    situacao_compra_nome: str | None = Field(default=None, alias="situacaoCompraNome")
    srp: bool | None = None
    data_publicacao_pncp: datetime | None = Field(
        default=None, alias="dataPublicacaoPncp"
    )
    data_abertura_proposta: datetime | None = Field(
        default=None, alias="dataAberturaProposta"
    )
    data_encerramento_proposta: datetime | None = Field(
        default=None, alias="dataEncerramentoProposta"
    )
    valor_total_estimado: float | None = Field(default=None, alias="valorTotalEstimado")
    valor_total_homologado: float | None = Field(
        default=None, alias="valorTotalHomologado"
    )
    link_sistema_origem: str | None = Field(default=None, alias="linkSistemaOrigem")
    orgao_entidade: PNCPOrganization | None = Field(default=None, alias="orgaoEntidade")
    unidade_orgao: PNCPUnit | None = Field(default=None, alias="unidadeOrgao")

    @field_validator(
        "data_publicacao_pncp",
        "data_abertura_proposta",
        "data_encerramento_proposta",
        mode="before",
    )
    @classmethod
    def empty_datetime_as_none(cls, value: Any) -> Any:
        return None if value == "" else value


class PNCPPage(PNCPModel):
    data: list[PNCPContracting] = Field(default_factory=list)
    total_registros: int = Field(default=0, alias="totalRegistros")
    total_paginas: int = Field(default=0, alias="totalPaginas")
    numero_pagina: int = Field(default=1, alias="numeroPagina")
    paginas_restantes: int = Field(default=0, alias="paginasRestantes")
    empty: bool = False


class PNCPSearchRequest(BaseModel):
    palavra_chave: str | None = Field(default=None, min_length=2, max_length=200)
    data_inicial: date
    data_final: date
    codigo_modalidade_contratacao: int
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    pagina: int = Field(default=1, ge=1)
    somente_srp: bool = False

    @field_validator("uf")
    @classmethod
    def normalize_uf(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else None

    @field_validator("data_final")
    @classmethod
    def validate_date_range(cls, value: date, info: Any) -> date:
        start = info.data.get("data_inicial")
        if start and value < start:
            raise ValueError("data_final deve ser maior ou igual a data_inicial")
        if start and (value - start).days > 365:
            raise ValueError("o período máximo de consulta é de 365 dias")
        return value


class PNCPSearchResponse(BaseModel):
    fonte: str = "PNCP"
    endpoint: str
    parametros: dict[str, Any]
    total_registros_fonte: int
    total_paginas_fonte: int
    pagina_fonte: int
    total_itens_retornados: int
    filtro_local_aplicado: bool
    itens: list[PNCPContracting]
