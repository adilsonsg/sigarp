# Aplicação do pacote da Sprint 2

1. Execute `docker compose down`.
2. Extraia o ZIP.
3. Copie todos os arquivos de dentro da pasta extraída para a raiz do repositório SIGARP.
4. Autorize a substituição dos arquivos existentes.
5. Execute:

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose run --rm backend pytest -v
```

6. Abra `http://127.0.0.1:8000/docs`.

Commit sugerido:

```text
feat: adiciona persistência e API de órgãos
```
