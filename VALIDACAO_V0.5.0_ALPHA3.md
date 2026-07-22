# Validação — SIGARP v0.5.0-alpha3

## Resultado automatizado

- 46 testes aprovados com `pytest -q`;
- sintaxe validada com `python -m compileall`;
- migrações Alembic executadas até `20260721_0005 (head)` em banco limpo;
- classificação de amostras validada:
  - item com projetor: `CONFIRMADA_ITEM`;
  - objeto com projetor e itens genéricos: `CANDIDATA_DOCUMENTO`;
  - caixa de som multimídia: `DESCARTADA_FALSO_POSITIVO`;
  - veículo com kit multimídia: `DESCARTADA_FALSO_POSITIVO`.

## Fluxo operacional

1. executar a migração;
2. classificar as contratações existentes;
3. sincronizar documentos das candidatas;
4. reclassificar;
5. consultar `/pncp/oportunidades`.
