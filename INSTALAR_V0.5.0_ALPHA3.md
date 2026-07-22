# Instalação — SIGARP v0.5.0-alpha3

## Entregas

- sincronização dos metadados de documentos das contratações PNCP;
- classificação automática de oportunidades para projetores;
- API `GET /pncp/oportunidades`;
- persistência das classificações e evidências;
- migração Alembic `20260721_0005`.

## Atualização

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -q
```

## Classificação inicial

```powershell
docker compose exec backend python -m app.cli.classify_pncp_opportunities
```

## Documentos apenas das candidatas

```powershell
docker compose exec backend python -m app.cli.sync_pncp_documents `
  --somente-candidatas `
  --somente-sem-documentos `
  --intervalo-requisicoes 3
```

## Reclassificação após sincronizar documentos

```powershell
docker compose exec backend python -m app.cli.classify_pncp_opportunities
```

## Consulta

```powershell
Invoke-RestMethod `
  "http://localhost:8000/pncp/oportunidades?classificacao=CANDIDATA_DOCUMENTO&uf=MT"
```
