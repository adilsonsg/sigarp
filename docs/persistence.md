# Persistência de atas de registro de preços

A versão `0.4.0-alpha2` adiciona a base do índice local do SIGARP.

## Entidades

- `organizations`: órgãos gerenciadores;
- `suppliers`: fornecedores normalizados por CNPJ;
- `price_registry_records`: atas identificadas pelo número de controle PNCP;
- `price_registry_items`: itens, marca, fabricante, modelo, quantidade e valor.

O campo `dados_fonte` preserva o JSON original para auditoria e reprocessamento.

## Migração

```bash
alembic upgrade head
```

## UPSERT

`PriceRegistryRepository.upsert()` usa `numero_controle_pncp` como chave estável. Uma nova coleta atualiza a ata existente e substitui seus itens, evitando duplicidade.

## Limite desta entrega

Esta versão cria o modelo, a migração e o repositório. A sincronização automática da API PNCP será implementada na próxima etapa.
