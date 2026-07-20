# Correção Sprint 3A M2 — alpha2-fix1

Esta correção não altera os endpoints públicos. Ela centraliza a infraestrutura HTTP
reutilizável e corrige a versão informada ao container Docker.

## Aplicação

1. Copie os arquivos deste pacote sobre o repositório atual.
2. Execute:

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
```

3. Valide:

```powershell
docker compose exec backend printenv APP_VERSION
docker compose run --rm backend pytest -v
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

O valor de `APP_VERSION` deve ser `0.3.0-alpha2`.
