# Instalação — Sprint 3A M1

## 1. Criar a branch

```powershell
git switch main
git pull
git switch -c feature/sprint-3a-pncp-collector
```

## 2. Aplicar o pacote

Copie o conteúdo deste pacote sobre a raiz do repositório SIGARP, permitindo a
substituição dos arquivos existentes.

## 3. Reconstruir os contêineres

```powershell
docker compose down
docker compose up -d --build
```

Não há nova migration de banco nesta entrega.

## 4. Validar

```powershell
docker compose run --rm backend pytest
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

## 5. Versionar

```powershell
git add .
git commit -m "feat: adiciona infraestrutura base do coletor PNCP"
git push -u origin feature/sprint-3a-pncp-collector
```

A tag `v0.3.0-alpha1` deve ser criada somente após revisão e merge na branch
principal.
