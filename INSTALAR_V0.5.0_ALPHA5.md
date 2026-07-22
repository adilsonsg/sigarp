# Instalação SIGARP v0.5.0-alpha5

1. Aplique o patch sobre a v0.5.0-alpha4.
2. Reconstrua o backend.
3. Execute `alembic upgrade head`.
4. Rode `pytest -q`.
5. Reclassifique as oportunidades.

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -q
docker compose exec backend python -m app.cli.classify_pncp_opportunities
```

Consulta por adequação:

```powershell
Invoke-RestMethod "http://localhost:8000/pncp/oportunidades?adequacao=INCOMPATIVEL&uf=MT"
```
