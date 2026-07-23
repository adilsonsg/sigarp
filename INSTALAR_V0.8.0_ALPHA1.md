# Instalação — SIGARP v0.8.0-alpha1

## Escopo

Esta pré-release acrescenta controles de segurança e conformidade da entrega. Não
há nova migration de banco depois de `20260722_0010`.

Antes de atualizar:

- preserve o dump PostgreSQL e o arquivo local de segredos;
- confirme que `.env` está ignorado e não versionado;
- não reutilize credenciais expostas em terminal, chat ou histórico Git;
- trate a versão como alpha, não homologada para produção.

## Atualização

No PowerShell, a partir do repositório:

```powershell
git fetch origin --prune --tags
git status -sb
git switch main
git pull --ff-only origin main
git rev-parse HEAD
git rev-parse 'v0.8.0-alpha1^{}'
```

Os dois últimos hashes devem coincidir depois da publicação da tag.

Mantenha os valores locais existentes de `POSTGRES_PASSWORD` e
`AUTH_PRINCIPALS`. Atualize apenas a identificação de versão no `.env`, se esses
campos estiverem definidos:

```text
APP_VERSION=0.8.0-alpha1
PNCP_USER_AGENT=SIGARP/0.8.0-alpha1 (IFMT)
```

Recrie e atualize:

```powershell
docker compose build --no-cache backend
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
docker compose up -d backend
docker compose ps
```

Valide `/health` com:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

O resultado deve informar `version = 0.8.0-alpha1` e `status = online`.

## Release verificável

A GitHub Release deve conter:

- `SIGARP-0.8.0-alpha1-release.zip`;
- `SIGARP-v0.8.0-alpha1-sbom.spdx.json`;
- `SHA256SUMS-v0.8.0-alpha1.txt`.

Compare os hashes antes de distribuir o pacote. O ZIP vem diretamente da árvore
da tag e não contém `.env`, tokens, dumps ou arquivos ignorados.
