import argparse
import asyncio
import json
from datetime import date

from app.database.session import SessionLocal
from app.sync.pncp_sync import PNCPSyncService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sincroniza contratações do PNCP.")
    parser.add_argument("--inicio", type=date.fromisoformat, required=True)
    parser.add_argument("--fim", type=date.fromisoformat, required=True)
    parser.add_argument("--modalidade", type=int, required=True)
    parser.add_argument("--uf", type=str)
    parser.add_argument(
        "--todas", action="store_true", help="Inclui contratações sem SRP."
    )
    parser.add_argument("--limite-paginas", type=int)
    parser.add_argument("--pagina-inicial", type=int, default=1)
    parser.add_argument("--intervalo-paginas", type=float, default=2.0)
    return parser


async def run() -> None:
    args = build_parser().parse_args()
    if args.fim < args.inicio:
        raise SystemExit("--fim deve ser maior ou igual a --inicio")

    with SessionLocal() as db:
        stats = await PNCPSyncService(
            db, page_delay_seconds=args.intervalo_paginas
        ).synchronize(
            data_inicial=args.inicio,
            data_final=args.fim,
            codigo_modalidade_contratacao=args.modalidade,
            uf=args.uf,
            somente_srp=not args.todas,
            limite_paginas=args.limite_paginas,
            pagina_inicial=args.pagina_inicial,
        )
    print(json.dumps(stats.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
