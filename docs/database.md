# Banco de dados

## Tecnologia

PostgreSQL 16 com SQLAlchemy 2 e Alembic.

## Regras

- Alterações de esquema devem usar migrations.
- `Base.metadata.create_all()` é permitido apenas nos testes.
- A API não cria tabelas automaticamente em produção.
- Nomes técnicos de tabelas permanecem em inglês.
- Campos expostos ao usuário podem permanecer em português.

## Comandos

```bash
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1
```

## Entidades atuais

| Tabela | Responsabilidade |
|---|---|
| `organizations` | órgãos públicos cadastrados |
| `suppliers` | fornecedores presentes em registros importados |
| `price_registry_records` | atas e registros de preços |
| `price_registry_items` | itens vinculados aos registros de preços |
| `pncp_contractings` | contratações normalizadas e payload oficial preservado |
| `pncp_contracting_items` | itens oficiais de cada contratação |
| `pncp_contracting_documents` | metadados, hash e texto extraído dos documentos |
| `pncp_opportunity_assessments` | classificação, evidências e adequação técnica |

## Integridade das avaliações

Uma contratação pode possuir uma avaliação por combinação de `perfil` e
`perfil_versao`. A restrição
`uq_pncp_opportunity_contracting_profile_version` impede duplicidade sem apagar o
histórico de versões anteriores.

Avaliações originadas antes da alpha6 são identificadas como `legacy-alpha5`.
Novos processamentos de projetores usam o perfil `1.0.0`.

## Migração corrente

O head esperado é `20260722_0008`. O downgrade para 0007 consolida múltiplas
versões em um registro por contratação e perfil; portanto, não deve ser executado
em produção sem cópia de segurança e plano de reversão.
