# Instalação — SIGARP v0.5.0-alpha6

## Pré-requisitos

- Docker Engine com Docker Compose v2;
- portas 5432 e 8000 disponíveis;
- cópia de segurança do PostgreSQL antes de atualizar um ambiente existente.

## Instalação limpa

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
curl http://127.0.0.1:8000/health
```

A resposta de saúde deve informar a versão `0.5.0-alpha6`.

## Atualização desde a alpha5

```bash
docker compose down
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

A migração `20260722_0008` preserva avaliações anteriores com a versão
`legacy-alpha5`. Execute novamente a classificação para gerar avaliações com o
perfil neutro `1.0.0`:

```bash
docker compose exec backend python -m app.cli.classify_pncp_opportunities
```

## Verificação

```bash
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

Não execute `alembic downgrade` em produção: o retorno à revisão 0007 precisa
consolidar múltiplas versões por contratação e remove o histórico excedente.
