import argparse
import asyncio
import json

from app.database.session import SessionLocal
from app.sync.pncp_document_sync import PNCPDocumentSyncService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sincroniza metadados de documentos das contratações PNCP."
    )
    parser.add_argument("--numero-controle-pncp")
    parser.add_argument("--somente-sem-documentos", action="store_true")
    parser.add_argument("--somente-candidatas", action="store_true")
    parser.add_argument("--limite-contratacoes", type=int)
    parser.add_argument("--intervalo-requisicoes", type=float, default=2.0)
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    with SessionLocal() as db:
        stats = await PNCPDocumentSyncService(
            db,
            request_delay_seconds=args.intervalo_requisicoes,
        ).synchronize(
            numero_controle_pncp=args.numero_controle_pncp,
            somente_sem_documentos=args.somente_sem_documentos,
            somente_candidatas=args.somente_candidatas,
            limite_contratacoes=args.limite_contratacoes,
        )
    print(json.dumps(stats.model_dump(), indent=2, ensure_ascii=False))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
