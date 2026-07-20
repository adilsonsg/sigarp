# ADR-004 — Logging estruturado

## Status

Aceito.

## Decisão

Logs da aplicação serão emitidos em JSON e incluirão:

- timestamp;
- nível;
- logger;
- mensagem;
- identificador de requisição;
- método;
- caminho;
- status;
- duração.

## Consequências

- Facilidade de auditoria.
- Integração futura com ferramentas de observabilidade.
- Correlação de eventos por requisição.
