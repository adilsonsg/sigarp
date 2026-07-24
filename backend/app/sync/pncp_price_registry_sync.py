import asyncio
import logging
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.schemas import PNCPPriceRegistry, PNCPPriceRegistryPage
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.pncp_price_registry import PNCPPriceRegistrySyncStats
from app.schemas.price_registry import PriceRegistryRecordInput

logger = logging.getLogger(__name__)

SPHERES = {
    "F": "federal",
    "E": "estadual",
    "M": "municipal",
    "D": "distrital",
}


class PNCPPriceRegistrySyncService:
    def __init__(
        self,
        db: Session,
        client: PNCPClient | None = None,
        page_delay_seconds: float = 2.0,
    ) -> None:
        self.db = db
        self.registry_repository = PriceRegistryRepository(db)
        self.organization_repository = OrganizationRepository(db)
        self._client = client
        self.page_delay_seconds = max(page_delay_seconds, 0.0)
        self._organization_cache: dict[str, dict[str, Any] | None] = {}

    async def synchronize(
        self,
        *,
        data_inicial: date,
        data_final: date,
        esfera: str | None = "federal",
        cnpj_orgao: str | None = None,
        pagina_inicial: int = 1,
        limite_paginas: int | None = None,
    ) -> PNCPPriceRegistrySyncStats:
        stats = PNCPPriceRegistrySyncStats()
        owns_client = self._client is None
        client = self._client or PNCPClient()
        page_number = pagina_inicial

        try:
            while True:
                payload = await client.buscar_atas_por_vigencia(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pagina=page_number,
                    cnpj_orgao=cnpj_orgao,
                )
                page = self._parse_page(payload)
                stats.paginas_processadas += 1
                stats.paginas_fonte = page.total_paginas
                stats.registros_fonte = page.total_registros

                for item in page.data:
                    stats.lidas += 1
                    if (
                        not item.numero_controle_pncp_ata
                        or not item.objeto
                        or not item.cnpj_orgao
                    ):
                        stats.ignoradas += 1
                        continue
                    try:
                        organization_data = await self._organization(
                            client, item.cnpj_orgao, stats
                        )
                        if not organization_data:
                            stats.ignoradas += 1
                            continue
                        item_sphere = self._sphere(organization_data.get("esferaId"))
                        if esfera and item_sphere != esfera:
                            stats.ignoradas += 1
                            continue

                        organization = self.organization_repository.upsert_pncp(
                            cnpj=self._digits(item.cnpj_orgao),
                            nome=(
                                organization_data.get("razaoSocial")
                                or f"Órgão {self._digits(item.cnpj_orgao)}"
                            ),
                            esfera=item_sphere,
                        )
                        existed = (
                            self.registry_repository.get_by_control_number(
                                item.numero_controle_pncp_ata
                            )
                            is not None
                        )
                        self.registry_repository.upsert(
                            self._normalize(item, organization.id),
                            replace_items=False,
                        )
                        if existed:
                            stats.atualizadas += 1
                        else:
                            stats.inseridas += 1
                    except Exception:
                        logger.exception(
                            "Falha ao persistir ata PNCP",
                            extra={
                                "numero_controle_pncp": (item.numero_controle_pncp_ata)
                            },
                        )
                        stats.erros += 1
                        self.db.rollback()

                if page.total_paginas <= page_number:
                    break
                if (
                    limite_paginas is not None
                    and stats.paginas_processadas >= limite_paginas
                ):
                    break
                if self.page_delay_seconds:
                    await asyncio.sleep(self.page_delay_seconds)
                page_number += 1
        finally:
            if owns_client:
                await client.close()

        return stats

    async def _organization(
        self,
        client: PNCPClient,
        cnpj: str,
        stats: PNCPPriceRegistrySyncStats,
    ) -> dict[str, Any] | None:
        normalized = self._digits(cnpj)
        if normalized not in self._organization_cache:
            payload = await client.buscar_orgao(normalized)
            stats.orgaos_consultados += 1
            if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
                payload = payload["data"]
            self._organization_cache[normalized] = (
                payload if isinstance(payload, dict) else None
            )
        return self._organization_cache[normalized]

    @staticmethod
    def _parse_page(payload: Any) -> PNCPPriceRegistryPage:
        if not isinstance(payload, dict):
            return PNCPPriceRegistryPage()
        normalized = dict(payload)
        normalized["data"] = (
            payload.get("data") or payload.get("atas") or payload.get("content") or []
        )
        return PNCPPriceRegistryPage.model_validate(normalized)

    @staticmethod
    def _normalize(
        item: PNCPPriceRegistry,
        organization_id: int,
    ) -> PriceRegistryRecordInput:
        today = date.today()
        if item.cancelado:
            status = "cancelada"
        elif (
            item.vigencia_inicio
            and item.vigencia_fim
            and item.vigencia_inicio <= today <= item.vigencia_fim
        ):
            status = "vigente"
        else:
            status = "expirada"
        return PriceRegistryRecordInput(
            numero_controle_pncp=item.numero_controle_pncp_ata or "",
            numero_ata=item.numero_ata,
            numero_processo=item.numero_controle_pncp_compra,
            objeto=item.objeto or "",
            vigencia_inicio=item.vigencia_inicio,
            vigencia_fim=item.vigencia_fim,
            situacao=status,
            orgao_gerenciador_id=organization_id,
            dados_fonte=item.model_dump(by_alias=True, mode="json"),
        )

    @staticmethod
    def _sphere(value: Any) -> str:
        return SPHERES.get(str(value or "").upper(), "desconhecida")

    @staticmethod
    def _digits(value: str) -> str:
        return "".join(character for character in value if character.isdigit())
