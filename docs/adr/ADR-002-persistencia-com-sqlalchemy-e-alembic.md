# ADR-002 — Persistência com SQLAlchemy e Alembic

## Status

Aceito.

## Decisão

O SIGARP utilizará SQLAlchemy 2 para persistência e Alembic para versionar alterações no esquema PostgreSQL. A API não criará tabelas automaticamente em produção.

## Consequências

- Histórico auditável do banco.
- Ambientes reproduzíveis.
- Migrações reversíveis.
- Base adequada para CI/CD.
