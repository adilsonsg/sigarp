# Validação — SIGARP v0.11.0-alpha1

```powershell
docker compose build backend
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
docker compose run --rm backend alembic heads
```

Validação funcional:

```powershell
.\ATUALIZAR_ATAS.ps1 -LimitePaginas 1

$headers = @{ Authorization = "Bearer SEU_TOKEN_LOCAL" }
Invoke-RestMethod `
    "http://127.0.0.1:8000/api/v1/atas?termo=projetor&somente_vigentes=true&esfera=federal&page_size=10" `
    -Headers $headers
```

Na interface:

- selecionar **Atas vigentes**;
- pesquisar `projetor`;
- confirmar datas inicial e final;
- verificar órgão e esfera;
- exportar o CSV;
- confirmar que atas expiradas não aparecem com `somente_vigentes=true`.
