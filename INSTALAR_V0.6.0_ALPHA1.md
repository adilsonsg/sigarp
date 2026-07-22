# Instalação — SIGARP v0.6.0-alpha1

## Objetivo

Esta versão adiciona execuções auditáveis e histórico imutável das avaliações,
mantendo compatibilidade com o perfil neutro `1.0.0` da alpha6.

## Atualização desde v0.5.0-alpha6

Faça backup do PostgreSQL e preserve o arquivo `.env`.

```bash
docker compose down
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

O head esperado é `20260722_0009`.

Avaliações existentes recebem `analisador_versao=legacy-unknown`; documentos já
analisados recebem `extrator_versao=legacy-unknown`. Execute novamente a extração
e a classificação para registrar as versões correntes e criar a primeira
execução auditável:

```bash
docker compose exec backend python -m app.cli.analyze_pncp_documents
docker compose exec backend python -m app.cli.classify_pncp_opportunities
```

A resposta deve incluir `execucao_id` e `status_execucao=CONCLUIDA`.

## Validação

```bash
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

Não use `docker compose down -v`. O downgrade para 0008 remove o histórico da
Etapa 1 e só deve ser usado em ambiente descartável ou após backup.
