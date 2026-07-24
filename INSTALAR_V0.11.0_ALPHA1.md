# Instalação local — SIGARP v0.11.0-alpha1

Esta versão adiciona coleta e consulta de atas por vigência real. Não há nova
migration depois de `20260722_0010`.

## Atualização

```powershell
git switch main
git pull --ff-only origin main
docker compose build backend
docker compose run --rm backend alembic upgrade head
docker compose up -d backend
```

Preserve o `.env`, o arquivo de segredos e o backup PostgreSQL.

## Coleta inicial controlada

Colete uma página de atas federais vigentes hoje. Uma página do PNCP pode
conter 500 registros:

```powershell
.\ATUALIZAR_ATAS.ps1 -LimitePaginas 1
```

Depois de validar o volume e os resultados, amplie:

```powershell
.\ATUALIZAR_ATAS.ps1 -LimitePaginas 5
```

Abra `http://127.0.0.1:8000/consulta`, selecione **Atas vigentes** e informe uma
palavra-chave, como `projetor`.

## Regra de vigência

O sistema utiliza as datas de vigência informadas pelo PNCP. Uma ata de 2025
pode aparecer como vigente em 2026. A publicação antiga, sozinha, não significa
que a ata esteja válida ou disponível para adesão.
