# SIGARP

Sistema Inteligente de Gestão e Análise de Registro de Preços.

## Objetivo

Criar uma plataforma pública, neutra e auditável para localizar, analisar e comparar Atas de Registro de Preços com base em requisitos técnicos objetivos.

## Tecnologias iniciais

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2
- Alembic
- Docker Compose
- Pytest
- Ruff

## Executar com Docker

```bash
docker compose up --build
```

Depois acesse:

- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Resposta esperada:

```json
{
  "application": "SIGARP",
  "version": "0.1.0",
  "status": "online"
}
```

## Executar testes

```bash
docker compose run --rm backend pytest
```

## Estrutura

```text
backend/
  app/
    api/
    core/
    database/
    models/
    schemas/
    services/
  tests/
docs/
```
