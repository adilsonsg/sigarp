import asyncio
import logging
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.pncp.client import PNCPClient
from app.models.pncp_contracting import PNCPContractingRecord
from app.repositories.pncp_contracting_item_repository import (
    PNCPContractingItemRepository,
)
from app.schemas.pncp_items import PNCPContractingItemInput, PNCPItemSyncStats

logger = logging.getLogger(__name__)


class PNCPItemSyncService:
    def __init__(
        self,
        db: Session,
        client: PNCPClient | None = None,
        request_delay_seconds: float = 2.0,
    ) -> None:
        self.db = db
        self.repository = PNCPContractingItemRepository(db)
        self._client = client
        self.request_delay_seconds = max(request_delay_seconds, 0.0)

    async def synchronize(
        self,
        *,
        numero_controle_pncp: str | None = None,
        somente_sem_itens: bool = False,
        limite_contratacoes: int | None = None,
        tamanho_pagina: int = 100,
    ) -> PNCPItemSyncStats:
        stats = PNCPItemSyncStats()
        owns_client = self._client is None
        client = self._client or PNCPClient()
        try:
            for contracting in self._contractings(
                numero_controle_pncp, somente_sem_itens, limite_contratacoes
            ):
                identifiers = self._identifiers(contracting)
                if identifiers is None:
                    stats.ignorados += 1
                    continue
                cnpj, ano, sequencial = identifiers
                try:
                    pagina = 1
                    while True:
                        payload = await client.buscar_itens_contratacao(
                            cnpj=cnpj,
                            ano=ano,
                            sequencial=sequencial,
                            pagina=pagina,
                            tamanho_pagina=tamanho_pagina,
                        )
                        stats.paginas_processadas += 1
                        items, total_paginas = self._extract_page(payload)
                        for item in items:
                            stats.itens_lidos += 1
                            normalized = self._normalize(contracting.id, item)
                            if normalized is None:
                                stats.ignorados += 1
                                continue
                            _, created = self.repository.upsert(normalized)
                            if created:
                                stats.inseridos += 1
                            else:
                                stats.atualizados += 1
                        self.db.commit()
                        if pagina >= total_paginas:
                            break
                        pagina += 1
                        if self.request_delay_seconds:
                            await asyncio.sleep(self.request_delay_seconds)
                    stats.contratacoes_processadas += 1
                except Exception:
                    logger.exception(
                        "Falha ao sincronizar itens PNCP",
                        extra={
                            "numero_controle_pncp": contracting.numero_controle_pncp
                        },
                    )
                    stats.erros += 1
                    self.db.rollback()
                if self.request_delay_seconds:
                    await asyncio.sleep(self.request_delay_seconds)
        finally:
            if owns_client:
                await client.close()
        return stats

    def _contractings(
        self, control_number: str | None, only_without_items: bool, limit: int | None
    ):
        statement = select(PNCPContractingRecord).order_by(PNCPContractingRecord.id)
        if control_number:
            statement = statement.where(
                PNCPContractingRecord.numero_controle_pncp == control_number
            )
        if only_without_items:
            statement = statement.where(~PNCPContractingRecord.items.any())
        if limit:
            statement = statement.limit(limit)
        return list(self.db.scalars(statement))

    @staticmethod
    def _identifiers(record: PNCPContractingRecord) -> tuple[str, int, int] | None:
        raw = record.dados_fonte or {}
        cnpj = record.orgao_cnpj or ((raw.get("orgaoEntidade") or {}).get("cnpj"))
        ano = record.ano_compra or raw.get("anoCompra")
        sequencial = raw.get("sequencialCompra")
        if sequencial is None:
            try:
                sequencial = int(
                    record.numero_controle_pncp.split("-1-")[1].split("/")[0]
                )
            except (IndexError, ValueError):
                return None
        if not cnpj or not ano:
            return None
        return str(cnpj), int(ano), int(sequencial)

    @staticmethod
    def _extract_page(payload: Any) -> tuple[list[dict[str, Any]], int]:
        if isinstance(payload, list):
            return payload, 1
        if not isinstance(payload, dict):
            return [], 1
        items = payload.get("data") or payload.get("itens") or []
        total_pages = payload.get("totalPaginas") or payload.get("total_paginas") or 1
        return list(items), max(int(total_pages or 1), 1)

    @staticmethod
    def _decimal(value: Any) -> Decimal | None:
        return Decimal(str(value)) if value is not None else None

    @classmethod
    def _normalize(
        cls, contracting_id: int, item: dict[str, Any]
    ) -> PNCPContractingItemInput | None:
        numero_item = item.get("numeroItem")
        descricao = item.get("descricao")
        if numero_item is None or not descricao:
            return None
        return PNCPContractingItemInput(
            contracting_id=contracting_id,
            numero_item=int(numero_item),
            descricao=str(descricao),
            material_ou_servico=item.get("materialOuServico"),
            material_ou_servico_nome=item.get("materialOuServicoNome"),
            quantidade=cls._decimal(item.get("quantidade")),
            unidade_medida=item.get("unidadeMedida"),
            valor_unitario_estimado=cls._decimal(item.get("valorUnitarioEstimado")),
            valor_total=cls._decimal(item.get("valorTotal")),
            situacao_item_id=item.get("situacaoCompraItemId"),
            situacao_item_nome=item.get("situacaoCompraItemNome"),
            criterio_julgamento_id=item.get("criterioJulgamentoId"),
            criterio_julgamento_nome=item.get("criterioJulgamentoNome"),
            tem_resultado=item.get("temResultado"),
            orcamento_sigiloso=item.get("orcamentoSigiloso"),
            informacao_complementar=item.get("informacaoComplementar"),
            catalogo_codigo_item=item.get("catalogoCodigoItem"),
            dados_fonte=item,
        )
