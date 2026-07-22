# Validação — SIGARP v0.6.0-alpha1

## Critérios de aceite

| Controle | Evidência esperada |
|---|---|
| Versão | `/health` retorna `0.6.0-alpha1` |
| Banco | head `20260722_0009` |
| Execução | classificação retorna ID e status concluído |
| Histórico | duas classificações criam duas execuções e dois snapshots |
| Estado corrente | permanece uma avaliação por contratação, perfil e versão |
| Evidência | documento expõe URL/URI, SHA-256, versão do extrator e datas de coleta/origem/análise |
| Requisitos | resultado por requisito referencia os trechos utilizados |
| API | endpoints de execuções e histórico respondem com versões utilizadas |
| Qualidade | Pytest, Ruff, Black e isort aprovados |

## Consultas operacionais

```http
GET /pncp/oportunidades/execucoes
GET /pncp/oportunidades/{assessment_id}/historico
```

## Resultado local

- Testes: 60 aprovados
- Migração: `0008 → 0009 → 0008 → 0009` aprovada em SQLite
- Dados alpha6: preservados com analisador/extrator `legacy-unknown`
- Reprocessamento: estado corrente preservado e snapshots acumulados
- PostgreSQL: validar antes da publicação da tag
