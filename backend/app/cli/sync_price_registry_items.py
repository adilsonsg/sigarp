import argparse
import asyncio
import json

from app.collectors.pncp.client import PNCPClient
from app.database.session import SessionLocal
from app.sync.comprasgov_price_registry_item_sync import (
    ComprasGovPriceRegistryItemSyncService,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sincroniza itens das atas federais via Compras.gov.br."
    )
    parser.add_argument("--atualizar-existentes", action="store_true")
    parser.add_argument("--limite-atas", type=int)
    parser.add_argument("--intervalo-requisicoes", type=float, default=1.0)
    return parser


async def run(args: argparse.Namespace) -> None:
    with SessionLocal() as db:
        async with PNCPClient() as client:
            service = ComprasGovPriceRegistryItemSyncService(
                db,
                client=client,
                request_delay_seconds=args.intervalo_requisicoes,
            )
            stats = await service.synchronize(
                only_without_items=not args.atualizar_existentes,
                limit=args.limite_atas,
            )
    print(json.dumps(stats.model_dump(), ensure_ascii=False, indent=2))


def main() -> None:
    asyncio.run(run(build_parser().parse_args()))


if __name__ == "__main__":
    main()
