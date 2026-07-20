# SIGARP v0.4.0-alpha1

## Aplicação

1. Faça backup do projeto atual.
2. Copie o conteúdo da pasta `sigarp` sobre o repositório local.
3. Reconstrua o backend:

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
```

## Validação

```powershell
docker compose exec backend printenv APP_VERSION
curl.exe http://127.0.0.1:8000/health
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

Versão esperada: `0.4.0-alpha1`.

## Nova consulta

Abra o Swagger em `http://127.0.0.1:8000/docs` e teste `GET /pncp/search`.
