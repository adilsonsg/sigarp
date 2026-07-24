from datetime import date

from pydantic import BaseModel


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


class PNCPPriceRegistryOrganizationResponse(BaseModel):
    nome: str
    cnpj: str | None = None
    esfera: str
    uf: str | None = None
    municipio: str | None = None


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
    possibilidade_adesao: bool | None = None
