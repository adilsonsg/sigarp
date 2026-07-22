# Instalação SIGARP v0.5.0-alpha4

## Atualização

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -q
```

## Analisar documentos das oportunidades candidatas

```powershell
docker compose exec backend python -m app.cli.analyze_pncp_documents `
  --somente-candidatas `
  --somente-pendentes `
  --intervalo-requisicoes 3
```

## Reclassificar

```powershell
docker compose exec backend python -m app.cli.classify_pncp_opportunities
```

## Consultar confirmações documentais

```powershell
Invoke-RestMethod `
  "http://localhost:8000/pncp/oportunidades?classificacao=CONFIRMADA_DOCUMENTO&uf=MT"
```
