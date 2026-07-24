# Validação — SIGARP v0.12.0-alpha1

## Automação

- 86 testes automatizados;
- Ruff, Black e isort;
- sintaxe JavaScript;
- migração head `20260724_0011`.

## Fonte real

Foi consultada uma ata federal real no módulo ARP do Compras.gov.br. Dois itens
foram lidos e persistidos com quantidade registrada, empenhada, saldo estimado,
limite de adesão, valor unitário e fornecedor, sem erros.

## PostgreSQL local

Após aplicar o patch:

```powershell
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend alembic current
docker compose run --rm backend pytest -q
```

O resultado esperado do Alembic é `20260724_0011 (head)`.

Execute a coleta e teste uma quantidade:

```powershell
.\ATUALIZAR_ATAS.ps1 -LimitePaginas 1 -LimiteAtasItens 100
```

Na interface, pesquise `notebook` com quantidade mínima `20`. Itens sem limite
positivo de adesão devem aparecer como **Confirmar com órgão**, e não como
disponibilidade garantida.
