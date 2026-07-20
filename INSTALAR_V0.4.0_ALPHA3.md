# SIGARP v0.4.0-alpha3

Esta versão adiciona sincronização paginada das contratações publicadas no PNCP para o PostgreSQL, com UPSERT e filtro padrão para SRP.

## Aplicação

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
```

## Sincronização

```powershell
docker compose exec backend python -m app.cli.sync_pncp --inicio 2026-07-01 --fim 2026-07-20 --modalidade 6 --uf MT
```

Para teste controlado, acrescente `--limite-paginas 1`. Para incluir contratações sem SRP, use `--todas`.

## Validação

```powershell
docker compose exec backend printenv APP_VERSION
docker compose run --rm backend pytest -q
```

Versão esperada: `0.4.0-alpha3`.
