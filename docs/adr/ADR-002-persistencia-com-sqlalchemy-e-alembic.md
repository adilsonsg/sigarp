# ADR-002 — Persistência com SQLAlchemy e Alembic

## Status

Aceito.

## Decisão

SQLAlchemy 2 será usado como ORM e Alembic para versionamento do esquema.
A API não criará tabelas automaticamente em produção.
