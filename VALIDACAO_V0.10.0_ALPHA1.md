# Validação — SIGARP v0.10.0-alpha1

## Validações automatizadas

```powershell
docker compose build backend
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
docker compose run --rm backend alembic heads
```

## Validação local

```powershell
.\INICIAR_SIGARP.ps1
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/health"
Invoke-WebRequest "http://127.0.0.1:8000/consulta" -UseBasicParsing |
    Select-Object StatusCode, ContentType
```

Resultado esperado:

- API `online`, versão `0.10.0-alpha1`;
- página de consulta com HTTP `200`;
- token de leitor aceito e token inválido rejeitado;
- filtros, paginação, detalhes e CSV funcionais.

Esta interface é destinada a consulta local individual. SUAP, SSO, gestão
institucional de usuários e implantação pública permanecem fora da entrega.
