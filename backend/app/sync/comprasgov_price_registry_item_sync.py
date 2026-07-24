import asyncio
import logging
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.schemas import ComprasGovPriceRegistryItem
from app.repositories.price_registry_repository import PriceRegistryRepository
from app.schemas.pncp_price_registry import (
    ComprasGovPriceRegistryItemSyncStats,
)
from app.schemas.price_registry import PriceRegistryItemInput, SupplierInput

logger = logging.getLogger(__name__)


class ComprasGovPriceRegistryItemSyncService:
    def __init__(
        self,
        db: Session,
        client: PNCPClient | None = None,
        request_delay_seconds: float = 1.0,
    ) -> None:
        self.db = db
        self.repository = PriceRegistryRepository(db)
        self._client = client
        self.request_delay_seconds = max(request_delay_seconds, 0.0)

    async def synchronize(
        self,
        *,
        only_without_items: bool = True,
        limit: int | None = None,
    ) -> ComprasGovPriceRegistryItemSyncStats:
        stats = ComprasGovPriceRegistryItemSyncStats()
        records = self.repository.list_for_item_sync(
            only_without_items=only_without_items,
            limit=limit,
        )
        owns_client = self._client is None
        client = self._client or PNCPClient()
        try:
            for position, record in enumerate(records):
                stats.atas_processadas += 1
                try:
                    payload = await client.buscar_itens_ata(record.numero_controle_pncp)
                    source_items = self._parse_items(payload)
                    stats.itens_lidos += len(source_items)
                    normalized = self._normalize_items(source_items)
                    if not normalized:
                        stats.atas_sem_itens += 1
                    else:
                        self.repository.replace_items(record, normalized)
                        stats.atas_com_itens += 1
                        stats.itens_armazenados += len(normalized)
                except Exception:
                    logger.exception(
                        "Falha ao sincronizar itens da ata",
                        extra={"numero_controle_pncp": record.numero_controle_pncp},
                    )
                    stats.erros += 1
                    self.db.rollback()
                if self.request_delay_seconds and position < len(records) - 1:
                    await asyncio.sleep(self.request_delay_seconds)
        finally:
            if owns_client:
                await client.close()
        return stats

    @staticmethod
    def _parse_items(payload: Any) -> list[ComprasGovPriceRegistryItem]:
        if not isinstance(payload, dict):
            return []
        raw_items = payload.get("resultado") or []
        if not isinstance(raw_items, list):
            return []
        return [
            ComprasGovPriceRegistryItem.model_validate(item)
            for item in raw_items
            if isinstance(item, dict)
        ]

    @classmethod
    def _normalize_items(
        cls,
        source_items: list[ComprasGovPriceRegistryItem],
    ) -> list[PriceRegistryItemInput]:
        selected: dict[int, ComprasGovPriceRegistryItem] = {}
        for item in source_items:
            if item.item_excluido or not item.numero_item or not item.descricao:
                continue
            try:
                number = int(item.numero_item)
            except ValueError:
                continue
            current = selected.get(number)
            if current is None or cls._rank(item) < cls._rank(current):
                selected[number] = item

        result: list[PriceRegistryItemInput] = []
        for number, item in sorted(selected.items()):
            registered = (
                item.quantidade_homologada_vencedor
                if item.quantidade_homologada_vencedor is not None
                else item.quantidade_homologada_item
            )
            committed = item.quantidade_empenhada or Decimal("0")
            estimated_balance = (
                max(registered - committed, Decimal("0"))
                if registered is not None
                else None
            )
            supplier_cnpj = cls._digits(item.fornecedor_cnpj)
            supplier = (
                SupplierInput(
                    cnpj=supplier_cnpj if len(supplier_cnpj) == 14 else None,
                    razao_social=item.fornecedor_nome,
                )
                if item.fornecedor_nome
                else None
            )
            result.append(
                PriceRegistryItemInput(
                    numero_item=number,
                    descricao=item.descricao,
                    quantidade_registrada=registered,
                    quantidade_empenhada=item.quantidade_empenhada,
                    saldo_estimado=estimated_balance,
                    limite_adesao=item.limite_adesao,
                    valor_unitario=item.valor_unitario,
                    fornecedor=supplier,
                    dados_fonte=item.model_dump(by_alias=True, mode="json"),
                )
            )
        return result

    @staticmethod
    def _rank(item: ComprasGovPriceRegistryItem) -> tuple[int, str]:
        classification = item.classificacao_fornecedor or "999999"
        return (0 if classification == "001" else 1, classification)

    @staticmethod
    def _digits(value: str | None) -> str:
        return "".join(character for character in (value or "") if character.isdigit())
