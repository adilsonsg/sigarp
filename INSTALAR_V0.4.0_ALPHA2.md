# SIGARP v0.4.0-alpha2

## Aplicação

1. Faça backup ou commit do projeto atual.
2. Copie o conteúdo deste pacote sobre o diretório do SIGARP.
3. Recrie o backend e aplique as migrações.

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
```

## Validação

```powershell
docker compose exec backend printenv APP_VERSION
curl.exe http://127.0.0.1:8000/health
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
```

Versão esperada: `0.4.0-alpha2`.

## Banco de dados

A migração `20260720_0002` cria:

- `suppliers`;
- `price_registry_records`;
- `price_registry_items`.

Esta entrega ainda não inicia a sincronização automática com o PNCP. Ela prepara a persistência e o UPSERT necessários para essa próxima etapa.
