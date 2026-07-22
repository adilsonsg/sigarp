import argparse
import json

from app.database.session import SessionLocal
from app.services.pncp_opportunity_service import PNCPOpportunityService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classifica oportunidades PNCP para o perfil de projetores."
    )
    parser.add_argument("--perfil", default="projetores")
    parser.add_argument("--limite-contratacoes", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with SessionLocal() as db:
        stats = PNCPOpportunityService(db).classify_all(
            perfil=args.perfil,
            limite_contratacoes=args.limite_contratacoes,
        )
    print(json.dumps(stats.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
