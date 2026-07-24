# Instalação local — SIGARP v0.12.0-alpha1

Esta versão adiciona a migração `20260724_0011` e coleta itens de atas
federais no Compras.gov.br.

```powershell
docker compose build backend
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend pytest -q
docker compose up -d --force-recreate backend
```

Confirme:

```powershell
docker compose run --rm backend alembic current
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/health"
```

Atualize inicialmente até 100 atas:

```powershell
.\ATUALIZAR_ATAS.ps1 `
    -VigenteEm (Get-Date) `
    -Esfera federal `
    -LimitePaginas 1 `
    -LimiteAtasItens 100
```

Abra `http://127.0.0.1:8000/consulta`, selecione **Atas vigentes**, informe uma
palavra-chave e a quantidade mínima desejada.
