# Validação — SIGARP v0.5.0-alpha6

## Matriz de aceite

| Controle | Evidência esperada |
|---|---|
| Versão | `/health` retorna `0.5.0-alpha6` |
| Migração | `alembic heads` e `alembic current` indicam `20260722_0008` |
| Neutralidade | teste com fabricantes distintos retorna avaliação idêntica |
| Histórico | versões `legacy-alpha5` e `1.0.0` coexistem para a mesma contratação |
| API | `/pncp/oportunidades` retorna `perfil_versao` e aceita o filtro homônimo |
| Qualidade | Pytest, Ruff, Black e isort sem falhas |

## Comandos

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend alembic heads
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

## Caso de regressão documental

Reprocessar a contratação `04264173000178-1-000054/2026` e confirmar que o item
21 continua `INCOMPATIVEL` por fonte de luz com lâmpada UHE, resolução nativa
1280 × 800 e quantidade total inferior a 20. Nenhuma marca ou família comercial
deve aparecer nos requisitos, na pontuação ou nas observações da avaliação.

## Registro da execução

- Data: 2026-07-22
- Banco da validação: SQLite, instalação limpa e atualização desde 0007
- Testes aprovados: 59 de 59
- Qualidade: Ruff, Black e isort aprovados
- Migrações: `0007 → 0008 → 0007 → 0008` aprovadas
- Dados legados: convertidos para `legacy-alpha5`
- Histórico: versões `legacy-alpha5` e `1.0.0` coexistiram conforme esperado
- Restrição única: duplicidade por contratação, perfil e versão bloqueada
- Compilação: `python -m compileall` aprovada
- Commit: preencher após revisão e integração
