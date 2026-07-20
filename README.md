# SIGARP

Sistema Inteligente de Gestão e Análise de Registro de Preços.

## Versão atual

`0.2.0` — persistência, Alembic e API de órgãos.

## Instalação da Sprint 2

```bash
docker compose down
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose run --rm backend pytest -v
```

## Acessos

- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Endpoints

- `POST /orgaos`
- `GET /orgaos`
- `GET /orgaos/{id}`

Exemplo de cadastro:

```json
{
  "nome": "Instituto Federal de Mato Grosso",
  "sigla": "IFMT",
  "cnpj": "10784782000150",
  "esfera": "federal",
  "uf": "MT",
  "municipio": "Cuiabá"
}
```

## Migrações

```bash
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1
```
