# ADR-001 — Separação entre dados brutos e dados normalizados

## Status

Aceito.

## Contexto

O SIGARP precisa preservar documentos e dados oficiais exatamente como foram obtidos, ao mesmo tempo em que produz informações estruturadas para pesquisa e comparação.

## Decisão

Dados brutos serão armazenados separadamente dos dados normalizados.

A interpretação, extração ou classificação nunca substituirá o conteúdo original.

## Consequências

- Maior rastreabilidade.
- Possibilidade de auditoria.
- Reprocessamento futuro.
- Redução do risco de perda ou distorção do dado oficial.
