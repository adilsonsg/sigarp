# SIGARP v0.5.0-alpha1 — Itens PNCP

## Atualização

```powershell
docker compose down
docker compose build --no-cache backend
docker compose up -d --force-recreate
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -q
```

## Teste direcionado no processo do SENAR/MT

```powershell
docker compose exec backend python -m app.cli.sync_pncp_items `
  --numero-controle-pncp "04264173000178-1-000054/2026" `
  --intervalo-requisicoes 3
```

## Consultar projetores encontrados

```powershell
docker compose exec postgres psql -U sigarp -d sigarp -P pager=off -c "
SELECT
  c.numero_controle_pncp,
  i.numero_item,
  LEFT(i.descricao, 180) AS descricao,
  i.quantidade,
  i.unidade_medida,
  i.valor_unitario_estimado
FROM pncp_contracting_items i
JOIN pncp_contractings c ON c.id = i.contracting_id
WHERE i.descricao ILIKE '%projetor%'
ORDER BY c.data_publicacao_pncp DESC, i.numero_item;
"
```

Para sincronizar gradualmente as contratações que ainda não possuem itens:

```powershell
docker compose exec backend python -m app.cli.sync_pncp_items `
  --somente-sem-itens `
  --limite-contratacoes 10 `
  --intervalo-requisicoes 3
```
