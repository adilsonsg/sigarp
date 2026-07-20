# SIGARP

Sistema Inteligente de Gestão e Análise de Registro de Preços.

## Versão

`0.2.1` — Sprint 2.1: consolidação da arquitetura, qualidade, logging e CI.

## Tecnologias

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2
- Alembic
- Docker Compose
- Pytest
- Ruff
- Black
- isort
- GitHub Actions

## Início rápido

```bash
docker compose down
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose run --rm backend pytest -v
```

Acessos:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Qualidade

```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

Para formatar:

```bash
docker compose run --rm backend black .
docker compose run --rm backend isort .
docker compose run --rm backend ruff check . --fix
```

## Endpoints atuais

- `GET /health`
- `POST /orgaos`
- `GET /orgaos`
- `GET /orgaos/{id}`

## Documentação

- `INSTALAR_SPRINT_2_1.md`
- `CHECKLIST_SPRINT_2_1.md`
- `docs/architecture.md`
- `docs/database.md`
- `docs/contributing.md`
- `docs/adr/`
