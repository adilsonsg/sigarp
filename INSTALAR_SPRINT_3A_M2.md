# SIGARP — Instalação da Sprint 3A M2

Versão: `0.3.0-alpha2`

## Objetivo

Adicionar a primeira pesquisa REST funcional sobre a API pública de consulta do PNCP, ainda sem persistência no PostgreSQL.

## Instalação

1. Pare os containers:

```powershell
docker compose down
```

2. Copie o conteúdo deste pacote sobre a raiz do repositório, autorizando a substituição dos arquivos.

3. Verifique se o `.env` contém:

```env
APP_VERSION=0.3.0-alpha2
PNCP_BASE_URL=https://pncp.gov.br/api/consulta
```

4. Reconstrua:

```powershell
docker compose build --no-cache backend
docker compose up -d --force-recreate
```

5. Valide:

```powershell
docker compose run --rm backend pytest -v
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

## Teste da API

Abra o Swagger:

```text
http://127.0.0.1:8000/docs
```

Use `POST /pncp/contratacoes/pesquisar` com o exemplo:

```json
{
  "palavra_chave": "projetor",
  "data_inicial": "2026-07-01",
  "data_final": "2026-07-20",
  "codigo_modalidade_contratacao": 6,
  "uf": "MT",
  "pagina": 1,
  "somente_srp": true
}
```

Observação: a API oficial filtra por período, modalidade, UF e página. A palavra-chave e o indicador de SRP são aplicados localmente aos registros da página recebida.
