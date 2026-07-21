import asyncio
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.parser import parse_contracting_page
from app.collectors.pncp.schemas import PNCPContracting
from app.repositories.pncp_contracting_repository import PNCPContractingRepository
from app.schemas.pncp_sync import PNCPContractingInput, PNCPSyncStats

logger = logging.getLogger(__name__)


class PNCPSyncService:
    def __init__(
        self,
        db: Session,
        client: PNCPClient | None = None,
        page_delay_seconds: float = 2.0,
    ) -> None:
        self.db = db
        self.repository = PNCPContractingRepository(db)
        self._client = client
        self.page_delay_seconds = max(page_delay_seconds, 0.0)

    async def synchronize(
        self,
        *,
        data_inicial: date,
        data_final: date,
        codigo_modalidade_contratacao: int,
        uf: str | None = None,
        somente_srp: bool = True,
        pagina_inicial: int = 1,
        limite_paginas: int | None = None,
    ) -> PNCPSyncStats:
        stats = PNCPSyncStats()
        owns_client = self._client is None
        client = self._client or PNCPClient()
        pagina = pagina_inicial

        try:
            while True:
                payload = await client.buscar_contratacoes_publicadas(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    codigo_modalidade_contratacao=codigo_modalidade_contratacao,
                    pagina=pagina,
                    uf=uf,
                )
                page = parse_contracting_page(payload)
                stats.paginas_processadas += 1

                for item in page.data:
                    stats.lidos += 1
                    if somente_srp and item.srp is not True:
                        stats.ignorados += 1
                        continue
                    if not item.numero_controle_pncp or not item.objeto_compra:
                        stats.ignorados += 1
                        continue

                    try:
                        normalized = self._normalize(item)
                        _, created = self.repository.upsert(normalized)
                        if created:
                            stats.inseridos += 1
                        else:
                            stats.atualizados += 1
                    except Exception:
                        logger.exception(
                            "Falha ao persistir contratação PNCP",
                            extra={"numero_controle_pncp": item.numero_controle_pncp},
                        )
                        stats.erros += 1
                        self.db.rollback()

                self.db.commit()

                if page.total_paginas <= pagina:
                    break
                if (
                    limite_paginas is not None
                    and stats.paginas_processadas >= limite_paginas
                ):
                    break
                if self.page_delay_seconds > 0:
                    await asyncio.sleep(self.page_delay_seconds)
                pagina += 1
        finally:
            if owns_client:
                await client.close()

        return stats

    @staticmethod
    def _normalize(item: PNCPContracting) -> PNCPContractingInput:
        organization = item.orgao_entidade
        unit = item.unidade_orgao
        return PNCPContractingInput(
            numero_controle_pncp=item.numero_controle_pncp or "",
            numero_compra=item.numero_compra,
            ano_compra=item.ano_compra,
            processo=item.processo,
            objeto_compra=item.objeto_compra or "",
            modalidade_id=item.modalidade_id,
            modalidade_nome=item.modalidade_nome,
            situacao_compra_nome=item.situacao_compra_nome,
            srp=item.srp,
            data_publicacao_pncp=item.data_publicacao_pncp,
            valor_total_estimado=(
                Decimal(str(item.valor_total_estimado))
                if item.valor_total_estimado is not None
                else None
            ),
            valor_total_homologado=(
                Decimal(str(item.valor_total_homologado))
                if item.valor_total_homologado is not None
                else None
            ),
            orgao_cnpj=_digits_only(organization.cnpj if organization else None),
            orgao_razao_social=(organization.razao_social if organization else None),
            unidade_nome=unit.nome_unidade if unit else None,
            uf=unit.uf_sigla.upper() if unit and unit.uf_sigla else None,
            municipio=unit.municipio_nome if unit else None,
            link_sistema_origem=item.link_sistema_origem,
            dados_fonte=item.model_dump(by_alias=True, mode="json"),
        )


def _digits_only(value: str | None) -> str | None:
    if not value:
        return None
    normalized = "".join(character for character in value if character.isdigit())
    return normalized or None
