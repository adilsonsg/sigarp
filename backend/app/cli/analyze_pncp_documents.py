import argparse
import asyncio
import json

from app.database.session import SessionLocal
from app.services.pncp_document_content_service import (
    PNCPDocumentContentService,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa e extrai o conteúdo dos documentos PNCP."
    )
    parser.add_argument("--numero-controle-pncp")
    parser.add_argument("--somente-candidatas", action="store_true")
    parser.add_argument("--somente-pendentes", action="store_true")
    parser.add_argument("--limite-documentos", type=int)
    parser.add_argument("--intervalo-requisicoes", type=float, default=2.0)
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    with SessionLocal() as db:
        stats = await PNCPDocumentContentService(
            db,
            request_delay_seconds=args.intervalo_requisicoes,
        ).analyze(
            numero_controle_pncp=args.numero_controle_pncp,
            somente_candidatas=args.somente_candidatas,
            somente_pendentes=args.somente_pendentes,
            limite_documentos=args.limite_documentos,
        )
    print(json.dumps(stats.model_dump(), indent=2, ensure_ascii=False))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
