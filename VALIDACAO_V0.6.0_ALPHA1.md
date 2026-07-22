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
- PostgreSQL 16.14: migração `0008 → 0009` aprovada com dados alpha6
- Qualidade em Docker: Pytest, Ruff, Black e isort aprovados
- Auditoria PostgreSQL: três execuções concluídas sem erros, com 254 snapshots
  imutáveis em cada execução e 508 avaliações correntes sem duplicação
- API: versão `0.6.0-alpha1`, execuções e histórico consultados com sucesso
- Cadeia documental: SHA-256 preservado; execuções 1 e 2 mantiveram
  `extrator_versao=legacy-unknown`, e a execução 3 registrou `1.0.0`
- Requisitos: seis resultados técnicos rastreados com trechos de origem

## Evidência de validação PostgreSQL

- Data: 2026-07-22
- Banco: PostgreSQL 16.14
- Head Alembic: `20260722_0009`
- Contratações processadas por execução: 254
- Erros por execução: 0
- Snapshot documental validado:
  `257be538019919644d432bf15a354b8f6cd9edd3762e19f80503785663ea668d`
