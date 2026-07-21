# SIGARP v0.4.0-alpha4 — correção de rate limit do PNCP

## Alterações

- Respeita o cabeçalho HTTP `Retry-After`.
- Usa backoff exponencial com jitter quando o cabeçalho não é informado.
- Configura 7 retries e backoff inicial de 5 segundos.
- Aguarda 2 segundos entre páginas por padrão.
- Permite retomar com `--pagina-inicial`.
- Permite configurar a pausa com `--intervalo-paginas`.

## Aplicação

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
```

## Teste controlado

```powershell
docker compose exec backend python -m app.cli.sync_pncp `
  --inicio 2026-07-20 `
  --fim 2026-07-20 `
  --modalidade 6 `
  --uf MT `
  --limite-paginas 1
```
