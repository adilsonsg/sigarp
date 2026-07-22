# SIGARP

Sistema Inteligente de Gestão e Análise de Registro de Preços.

## Versão

`0.5.0-alpha6` — busca PNCP, análise documental e avaliação por perfil técnico
objetivo, neutro e versionado.

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
- `POST /pncp/contratacoes/pesquisar`
- `GET /pncp/search`
- `GET /pncp/oportunidades`

## Avaliação técnica neutra

O perfil corrente está em
`backend/app/profiles/projectors_v1.json`. Ele contém somente requisitos técnicos
objetivos e sua versão é persistida com cada avaliação. Marcas, fabricantes e
famílias comerciais não participam da pontuação ou da classificação.

Uma alteração de critérios exige um novo arquivo e uma nova versão SemVer do
perfil; avaliações anteriores permanecem consultáveis por `perfil_versao`.

## Documentação

- `INSTALAR_V0.5.0_ALPHA6.md`
- `VALIDACAO_V0.5.0_ALPHA6.md`
- `docs/architecture.md`
- `docs/database.md`
- `docs/contributing.md`
- `docs/adr/`
- `docs/backlog/ETAPA_0_ISSUES.md`

A documentação interativa está disponível em `http://127.0.0.1:8000/docs`.
