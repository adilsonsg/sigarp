# Banco de dados

## Tecnologia

PostgreSQL 16 com SQLAlchemy 2 e Alembic.

## Regras

- Alterações de esquema devem usar migrations.
- `Base.metadata.create_all()` é permitido apenas nos testes.
- A API não cria tabelas automaticamente em produção.
- Nomes técnicos de tabelas permanecem em inglês.
- Campos expostos ao usuário podem permanecer em português.

## Comandos

```bash
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1
```

## Entidades atuais

### organizations

Representa órgãos públicos cadastrados no SIGARP.

Campos principais:

- `id`
- `nome`
- `sigla`
- `cnpj`
- `esfera`
- `uf`
- `municipio`
- `criado_em`
