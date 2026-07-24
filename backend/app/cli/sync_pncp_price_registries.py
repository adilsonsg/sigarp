import argparse
import asyncio
import json
from datetime import date

from app.database.session import SessionLocal
from app.sync.pncp_price_registry_sync import PNCPPriceRegistrySyncService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sincroniza atas do PNCP pelo período de vigência."
    )
    parser.add_argument("--inicio", type=date.fromisoformat, required=True)
    parser.add_argument("--fim", type=date.fromisoformat, required=True)
    parser.add_argument(
        "--esfera",
        choices=["federal", "estadual", "municipal", "distrital"],
        default="federal",
    )
    parser.add_argument("--todas-esferas", action="store_true")
    parser.add_argument("--cnpj-orgao")
    parser.add_argument("--limite-paginas", type=int)
    parser.add_argument("--pagina-inicial", type=int, default=1)
    parser.add_argument("--intervalo-paginas", type=float, default=2.0)
    return parser


async def run() -> None:
    args = build_parser().parse_args()
    if args.fim < args.inicio:
        raise SystemExit("--fim deve ser maior ou igual a --inicio")
    if (args.fim - args.inicio).days > 365:
        raise SystemExit("o período máximo de consulta é de 365 dias")

    with SessionLocal() as db:
        stats = await PNCPPriceRegistrySyncService(
            db,
            page_delay_seconds=args.intervalo_paginas,
        ).synchronize(
            data_inicial=args.inicio,
            data_final=args.fim,
            esfera=None if args.todas_esferas else args.esfera,
            cnpj_orgao=args.cnpj_orgao,
            limite_paginas=args.limite_paginas,
            pagina_inicial=args.pagina_inicial,
        )
    print(json.dumps(stats.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
