from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

OpportunityClassification = Literal[
    "CONFIRMADA_ITEM",
    "CONFIRMADA_DOCUMENTO",
    "CANDIDATA_DOCUMENTO",
    "DESCARTADA_FALSO_POSITIVO",
    "SEM_CORRESPONDENCIA",
]

ProfileSuitability = Literal[
    "ADEQUADA",
    "PARCIALMENTE_ADEQUADA",
    "INCOMPATIVEL",
    "EXIGE_ANALISE_HUMANA",
]


class PNCPOpportunityAssessmentInput(BaseModel):
    contracting_id: int
    perfil: str = Field(default="projetores", min_length=2, max_length=50)
    perfil_versao: str = Field(min_length=5, max_length=30)
    analisador_versao: str = Field(min_length=5, max_length=30)
    classificacao: OpportunityClassification
    pontuacao: int = Field(ge=0, le=100)
    termos_encontrados: list[str] = Field(default_factory=list)
    evidencias: dict[str, Any] = Field(default_factory=dict)
    adequacao_perfil: ProfileSuitability | None = None
    pontuacao_adequacao: int | None = Field(default=None, ge=0, le=100)
    requisitos_atendidos: list[str] = Field(default_factory=list)
    requisitos_nao_atendidos: list[str] = Field(default_factory=list)
    requisitos_nao_comprovados: list[str] = Field(default_factory=list)
    dados_estruturados: dict[str, Any] = Field(default_factory=dict)


class PNCPOpportunityClassificationStats(BaseModel):
    execucao_id: int | None = None
    status_execucao: str | None = None
    processadas: int = 0
    confirmadas_item: int = 0
    confirmadas_documento: int = 0
    candidatas_documento: int = 0
    descartadas_falso_positivo: int = 0
    sem_correspondencia: int = 0
    adequadas: int = 0
    parcialmente_adequadas: int = 0
    incompativeis: int = 0
    exigem_analise_humana: int = 0
    sem_avaliacao_tecnica: int = 0
    erros: int = 0


class PNCPOpportunityDocumentResponse(BaseModel):
    sequencial_documento: int
    titulo: str | None = None
    tipo_documento_nome: str | None = None
    url: str | None = None
    uri: str | None = None
    nome_arquivo: str | None = None
    conteudo_tipo: str | None = None
    conteudo_tamanho: int | None = None
    conteudo_sha256: str | None = None
    data_publicacao_pncp: datetime | None = None
    coletado_em: datetime | None = None
    extracao_status: str | None = None
    extrator_versao: str | None = None
    texto_caracteres: int | None = None
    paginas_extraidas: int | None = None
    conteudo_analisado_em: datetime | None = None


class PNCPOpportunityItemResponse(BaseModel):
    numero_item: int
    descricao: str
    quantidade: float | None = None
    unidade_medida: str | None = None


class PNCPOpportunityResponse(BaseModel):
    assessment_id: int
    contracting_id: int
    perfil: str
    perfil_versao: str
    analisador_versao: str
    ultima_execucao_id: int | None = None
    classificacao: OpportunityClassification
    pontuacao: int
    termos_encontrados: list[str]
    evidencias: dict[str, Any]
    adequacao_perfil: ProfileSuitability | None = None
    pontuacao_adequacao: int | None = None
    requisitos_atendidos: list[str] = Field(default_factory=list)
    requisitos_nao_atendidos: list[str] = Field(default_factory=list)
    requisitos_nao_comprovados: list[str] = Field(default_factory=list)
    dados_estruturados: dict[str, Any] = Field(default_factory=dict)
    classificado_em: datetime
    numero_controle_pncp: str
    orgao_razao_social: str | None = None
    uf: str | None = None
    municipio: str | None = None
    data_publicacao_pncp: datetime | None = None
    objeto_compra: str
    link_sistema_origem: str | None = None
    itens: list[PNCPOpportunityItemResponse] = Field(default_factory=list)
    documentos: list[PNCPOpportunityDocumentResponse] = Field(default_factory=list)


class PNCPProcessingRunResponse(BaseModel):
    id: int
    tipo: str
    status: str
    perfil: str | None = None
    perfil_versao: str | None = None
    analisador_versao: str | None = None
    parametros: dict[str, Any] = Field(default_factory=dict)
    estatisticas: dict[str, Any] = Field(default_factory=dict)
    erro: str | None = None
    iniciado_em: datetime
    concluido_em: datetime | None = None


class PNCPOpportunityHistoryResponse(BaseModel):
    id: int
    assessment_id: int
    contracting_id: int
    execucao_id: int
    perfil: str
    perfil_versao: str
    analisador_versao: str
    classificacao: OpportunityClassification
    pontuacao: int
    adequacao_perfil: ProfileSuitability | None = None
    pontuacao_adequacao: int | None = None
    snapshot: dict[str, Any]
    classificado_em: datetime
    criado_em: datetime
