import argparse
import asyncio
import json

from app.database.session import SessionLocal
from app.sync.pncp_item_sync import PNCPItemSyncService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sincroniza itens das contratações PNCP já armazenadas."
    )
    parser.add_argument("--numero-controle-pncp")
    parser.add_argument("--somente-sem-itens", action="store_true")
    parser.add_argument("--limite-contratacoes", type=int)
    parser.add_argument("--tamanho-pagina", type=int, default=100)
    parser.add_argument("--intervalo-requisicoes", type=float, default=2.0)
    return parser


async def run() -> None:
    args = build_parser().parse_args()
    with SessionLocal() as db:
        stats = await PNCPItemSyncService(
            db, request_delay_seconds=args.intervalo_requisicoes
        ).synchronize(
            numero_controle_pncp=args.numero_controle_pncp,
            somente_sem_itens=args.somente_sem_itens,
            limite_contratacoes=args.limite_contratacoes,
            tamanho_pagina=args.tamanho_pagina,
        )
    print(json.dumps(stats.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
