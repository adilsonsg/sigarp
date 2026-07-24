from datetime import date, datetime
from decimal import Decimal
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


class PNCPPriceRegistry(PNCPModel):
    numero_controle_pncp_ata: str | None = Field(
        default=None, alias="numeroControlePNCPAta"
    )
    numero_controle_pncp_compra: str | None = Field(
        default=None, alias="numeroControlePNCPCompra"
    )
    numero_ata: str | None = Field(default=None, alias="numeroAtaRegistroPreco")
    ano_ata: int | None = Field(default=None, alias="anoAta")
    data_assinatura: date | None = Field(default=None, alias="dataAssinatura")
    vigencia_inicio: date | None = Field(default=None, alias="vigenciaInicio")
    vigencia_fim: date | None = Field(default=None, alias="vigenciaFim")
    data_cancelamento: date | None = Field(default=None, alias="dataCancelamento")
    cancelado: bool = False
    data_publicacao_pncp: datetime | None = Field(
        default=None, alias="dataPublicacaoPncp"
    )
    data_atualizacao: datetime | None = Field(default=None, alias="dataAtualizacao")
    objeto: str | None = Field(default=None, alias="objetoContratacao")
    cnpj_orgao: str | None = Field(default=None, alias="cnpjOrgao")
    nome_orgao: str | None = Field(default=None, alias="nomeOrgao")
    possibilidade_adesao: bool | None = Field(default=None, alias="possibilidadeAdesao")

    @field_validator(
        "data_assinatura",
        "vigencia_inicio",
        "vigencia_fim",
        "data_cancelamento",
        "data_publicacao_pncp",
        "data_atualizacao",
        mode="before",
    )
    @classmethod
    def empty_price_registry_date_as_none(cls, value: Any) -> Any:
        return None if value == "" else value


class PNCPPriceRegistryPage(PNCPModel):
    data: list[PNCPPriceRegistry] = Field(default_factory=list)
    total_registros: int = Field(default=0, alias="totalRegistros")
    total_paginas: int = Field(default=0, alias="totalPaginas")
    numero_pagina: int = Field(default=1, alias="numeroPagina")
    paginas_restantes: int = Field(default=0, alias="paginasRestantes")


class ComprasGovPriceRegistryItem(PNCPModel):
    numero_controle_pncp_ata: str | None = Field(
        default=None, alias="numeroControlePncpAta"
    )
    numero_item: str | None = Field(default=None, alias="numeroItem")
    descricao: str | None = Field(default=None, alias="descricaoItem")
    tipo_item: str | None = Field(default=None, alias="tipoItem")
    quantidade_homologada_item: Decimal | None = Field(
        default=None, alias="quantidadeHomologadaItem"
    )
    quantidade_homologada_vencedor: Decimal | None = Field(
        default=None, alias="quantidadeHomologadaVencedor"
    )
    quantidade_empenhada: Decimal | None = Field(
        default=None, alias="quantidadeEmpenhada"
    )
    limite_adesao: Decimal | None = Field(default=None, alias="maximoAdesao")
    valor_unitario: Decimal | None = Field(default=None, alias="valorUnitario")
    fornecedor_cnpj: str | None = Field(default=None, alias="niFornecedor")
    fornecedor_nome: str | None = Field(default=None, alias="nomeRazaoSocialFornecedor")
    classificacao_fornecedor: str | None = Field(
        default=None, alias="classificacaoFornecedor"
    )
    item_excluido: bool = Field(default=False, alias="itemExcluido")
    codigo_item: int | None = Field(default=None, alias="codigoItem")
    codigo_pdm: int | None = Field(default=None, alias="codigoPdm")
    nome_pdm: str | None = Field(default=None, alias="nomePdm")


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
