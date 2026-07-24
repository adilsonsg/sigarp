# Instalação local — SIGARP v0.10.0-alpha1

Esta versão entrega um modo de consulta local, operado por uma única pessoa,
sem alterar a autenticação e a trilha de auditoria existentes.

## Pré-requisitos

- Windows 10 ou 11;
- Docker Desktop em execução;
- Git;
- `.env` configurado com `POSTGRES_PASSWORD` e `AUTH_PRINCIPALS`.

Faça backup do banco e do arquivo local de segredos antes de atualizar.

## Atualização

```powershell
git switch main
git pull --ff-only origin main
docker compose build backend
docker compose run --rm backend alembic upgrade head
```

Não há nova migration depois de `20260722_0010`.

## Uso diário

Inicie o sistema:

```powershell
.\INICIAR_SIGARP.ps1
```

O navegador abrirá em `http://127.0.0.1:8000/consulta`. Informe o token de
leitor criado na instalação da v0.7.0-alpha1. O token permanece somente na aba
atual do navegador.

Atualize os últimos 30 dias, usando modalidade `6` e somente SRP:

```powershell
.\ATUALIZAR_PNCP.ps1
```

Para restringir a Mato Grosso e consultar 90 dias:

```powershell
.\ATUALIZAR_PNCP.ps1 -Inicio (Get-Date).AddDays(-90) -Uf MT
```

Para incluir contratações sem SRP:

```powershell
.\ATUALIZAR_PNCP.ps1 -IncluirSemSrp
```

## Consulta

A interface permite filtrar, paginar, examinar itens e documentos, abrir a
publicação de origem e exportar todos os resultados filtrados em CSV.

Para encerrar:

```powershell
docker compose down
```

Não use `docker compose down -v`, pois `-v` remove o volume de dados.
