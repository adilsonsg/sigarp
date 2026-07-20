# Atualização para a Sprint 2.1

## 1. Criar uma branch

No GitHub Desktop, crie:

```text
feature/sprint-2-1-arquitetura
```

## 2. Parar os containers

```bash
docker compose down
```

## 3. Substituir os arquivos

Copie todo o conteúdo deste pacote para a raiz do repositório:

```text
C:\Users\ti\Documents\GitHub\sigarp
```

Autorize a substituição dos arquivos existentes.

## 4. Reconstruir

```bash
docker compose up -d --build
```

## 5. Aplicar migrations

```bash
docker compose exec backend alembic upgrade head
```

A Sprint 2.1 não cria uma nova tabela; a migration da Sprint 2 é preservada.

## 6. Executar os testes

```bash
docker compose run --rm backend pytest -v
```

## 7. Executar qualidade

```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

## 8. Validar a API

Abra:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## Commit sugerido

```text
chore: consolida arquitetura e automação de qualidade
```

## Tag sugerida

```text
v0.2.1
```
