# SIGARP

## Consulta local

Na v0.10.0-alpha1, inicie o ambiente no Windows com:

```powershell
.\INICIAR_SIGARP.ps1
```

A interface será aberta em `http://127.0.0.1:8000/consulta`. Ela oferece
filtros, detalhes e exportação CSV sem remover a autenticação da API. Para
atualizar os dados do PNCP dos últimos 30 dias:

```powershell
.\ATUALIZAR_PNCP.ps1
```

Consulte `INSTALAR_V0.11.0_ALPHA1.md` para instalação e coleta de atas.

### Atas vigentes

Na v0.11.0-alpha1, a opção **Atas vigentes** consulta registros coletados pelo
período real de vigência. Isso inclui atas de 2025 que ainda sejam válidas em
2026. Para atualizar as atas federais vigentes hoje:

```powershell
.\ATUALIZAR_ATAS.ps1
```

A data de publicação não é usada isoladamente como evidência de vigência.

Sistema Inteligente de Gestão e Análise de Registro de Preços.

## Versão

`0.9.0-alpha1` — API pública versionada, busca PNCP, avaliação técnica neutra,
trilha de auditoria, controle de acesso e segurança automatizada da entrega.

## Tecnologias

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2
- Alembic
- Docker Compose
- Pytest
- Ruff
- Black
- isort
- GitHub Actions
- Gitleaks, pip-audit e SBOM SPDX

## Início rápido

```bash
docker compose down
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose run --rm backend pytest -v
```

Acessos:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- API v1: http://127.0.0.1:8000/api/v1

## Qualidade

```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

Para formatar:

```bash
docker compose run --rm backend black .
docker compose run --rm backend isort .
docker compose run --rm backend ruff check . --fix
```

## API pública v1

- `GET /api/v1/health`
- `GET /api/v1/auth/me`
- `POST /api/v1/orgaos`
- `GET /api/v1/orgaos`
- `GET /api/v1/orgaos/{id}`
- `POST /api/v1/pncp/contratacoes/pesquisar`
- `GET /api/v1/pncp/search`
- `GET /api/v1/pncp/oportunidades`
- `GET /api/v1/pncp/oportunidades/execucoes`
- `GET /api/v1/pncp/oportunidades/{assessment_id}/historico`
- `PATCH /api/v1/pncp/oportunidades/{assessment_id}/revisao`
- `GET /api/v1/pncp/oportunidades/{assessment_id}/revisoes`

As coleções locais retornam `items`, `page`, `page_size`, `total` e
`total_pages`. Erros possuem `detail`, `code`, `request_id` e `errors`. As rotas
sem prefixo continuam disponíveis temporariamente e aparecem como depreciadas no
OpenAPI. Consulte `docs/api-versioning.md`.

## Controle de acesso

As rotas de dados exigem `Authorization: Bearer <token>`; `/health` e os
metadados OpenAPI permanecem públicos. O backend guarda apenas SHA-256 de tokens
fortes configurados por ambiente. Os
papéis são `leitor`, `analista` e `administrador`; revisão humana exige analista,
e cadastro administrativo exige administrador. Consulte `docs/security.md`.

## Segurança da entrega e conformidade

O CI verifica segredos, dependências e novas vulnerabilidades. Cada GitHub
Release recebe pacote produzido da tag, SBOM SPDX JSON e checksums SHA-256.
Dependências Python e Actions são acompanhadas semanalmente pelo Dependabot.

O inventário preliminar de dados está documentado, mas licença, base legal,
retenção, agentes de tratamento e aprovação de produção continuam como decisões
formais do IFMT. A versão alpha não deve ser tratada como homologada para
produção.

## Avaliação técnica neutra

O perfil corrente está em
`backend/app/profiles/projectors_v1.json`. Ele contém somente requisitos técnicos
objetivos e sua versão é persistida com cada avaliação. Marcas, fabricantes e
famílias comerciais não participam da pontuação ou da classificação.

Uma alteração de critérios exige um novo arquivo e uma nova versão SemVer do
perfil; avaliações anteriores permanecem consultáveis por `perfil_versao`.

Cada classificação em lote cria uma execução identificável. O estado corrente
permanece otimizado para consulta, enquanto snapshots imutáveis preservam o
resultado de cada reprocessamento e a versão do analisador utilizada.

## Documentação

- `INSTALAR_V0.9.0_ALPHA1.md`
- `VALIDACAO_V0.9.0_ALPHA1.md`
- `docs/api-versioning.md`
- `docs/architecture.md`
- `docs/database.md`
- `docs/security.md`
- `docs/supply-chain.md`
- `docs/compliance/data-inventory.md`
- `docs/compliance/institutional-decisions.md`
- `docs/contributing.md`
- `docs/adr/`
- `docs/backlog/ETAPA_0_ISSUES.md`

A documentação interativa está disponível em `http://127.0.0.1:8000/docs`.
