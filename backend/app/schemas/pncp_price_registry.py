from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PNCPPriceRegistrySyncStats(BaseModel):
    paginas_processadas: int = 0
    paginas_fonte: int = 0
    registros_fonte: int = 0
    lidas: int = 0
    inseridas: int = 0
    atualizadas: int = 0
    ignoradas: int = 0
    orgaos_consultados: int = 0
    erros: int = 0


class ComprasGovPriceRegistryItemSyncStats(BaseModel):
    atas_processadas: int = 0
    atas_com_itens: int = 0
    atas_sem_itens: int = 0
    itens_lidos: int = 0
    itens_armazenados: int = 0
    erros: int = 0


class PNCPPriceRegistryOrganizationResponse(BaseModel):
    nome: str
    cnpj: str | None = None
    esfera: str
    uf: str | None = None
    municipio: str | None = None


class PNCPPriceRegistryItemSupplierResponse(BaseModel):
    cnpj: str | None = None
    razao_social: str


class PNCPPriceRegistryItemResponse(BaseModel):
    numero_item: int
    descricao: str
    quantidade_registrada: Decimal | None = None
    quantidade_empenhada: Decimal | None = None
    saldo_estimado: Decimal | None = None
    limite_adesao: Decimal | None = None
    valor_unitario: Decimal | None = None
    fornecedor: PNCPPriceRegistryItemSupplierResponse | None = None
    disponibilidade: str


class PNCPPriceRegistryResponse(BaseModel):
    id: int
    numero_controle_pncp: str
    numero_ata: str | None = None
    numero_processo: str | None = None
    objeto: str
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    situacao: str | None = None
    url_pncp: str | None = None
    orgao: PNCPPriceRegistryOrganizationResponse
    itens_quantidade: int = 0
    itens: list[PNCPPriceRegistryItemResponse] = Field(default_factory=list)
    possibilidade_adesao: bool | None = None
