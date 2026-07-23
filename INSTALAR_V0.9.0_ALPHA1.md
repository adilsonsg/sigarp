# Instalação — SIGARP v0.9.0-alpha1

## Escopo

Esta pré-release introduz a API pública `/api/v1`, paginação padronizada,
contrato uniforme de erros e testes do OpenAPI. Não há nova migration depois de
`20260722_0010`.

Antes de atualizar:

- preserve o dump PostgreSQL e o arquivo local de segredos;
- mantenha `POSTGRES_PASSWORD` e `AUTH_PRINCIPALS` do ambiente atual;
- confirme que `.env` permanece ignorado;
- trate a versão como alpha, não homologada para produção.

## Atualização

No PowerShell, a partir do repositório:

```powershell
git fetch origin --prune --tags
git status -sb
git switch main
git pull --ff-only origin main
git rev-parse HEAD
git rev-parse 'v0.9.0-alpha1^{}'
```

Atualize somente a identificação da aplicação no `.env`, sem substituir os
segredos:

```text
APP_VERSION=0.9.0-alpha1
PNCP_USER_AGENT=SIGARP/0.9.0-alpha1 (IFMT)
```

Recrie e valide:

```powershell
docker compose build --no-cache backend
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
docker compose up -d backend
docker compose ps
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/health"
```

O resultado deve informar `version = 0.9.0-alpha1` e `status = online`.

## Migração de consumidores

Troque o prefixo das chamadas:

```text
/orgaos                  -> /api/v1/orgaos
/pncp/oportunidades      -> /api/v1/pncp/oportunidades
```

Listas locais deixam de retornar um array isolado e passam a retornar o envelope
`items`, `page`, `page_size`, `total` e `total_pages`. As rotas antigas continuam
ativas temporariamente conforme `docs/api-versioning.md`.
