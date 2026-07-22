# Pesquisa de contratações no PNCP

## Endpoint do SIGARP

- `POST /pncp/contratacoes/pesquisar`: compatibilidade com a busca inicial;
- `GET /pncp/search`: busca com parâmetros de consulta;
- `GET /pncp/oportunidades`: oportunidades classificadas e avaliadas.
- `GET /pncp/oportunidades/execucoes`: lotes de classificação auditáveis;
- `GET /pncp/oportunidades/{assessment_id}/historico`: snapshots anteriores.

O serviço consulta o recurso público do PNCP para contratações por data de publicação:

`GET /v1/contratacoes/publicacao`

## Parâmetros enviados à fonte

- `dataInicial`: data inicial em `YYYYMMDD`;
- `dataFinal`: data final em `YYYYMMDD`;
- `codigoModalidadeContratacao`: código da modalidade;
- `uf`: opcional;
- `pagina`: número da página.

## Filtros locais

A API oficial não recebe a palavra-chave usada pelo SIGARP neste fluxo. Por isso, `palavra_chave` é aplicada localmente aos campos de objeto, informação complementar, número da compra e processo da página retornada.

O filtro `somente_srp` também é aplicado localmente.

## Índice local

Os comandos de sincronização percorrem páginas, normalizam contratações e fazem
UPSERT pelo número de controle PNCP. Itens e documentos usam identificadores
próprios da fonte e podem ser sincronizados de forma idempotente.

```bash
python -m app.cli.sync_pncp
python -m app.cli.sync_pncp_items
python -m app.cli.sync_pncp_documents
python -m app.cli.analyze_pncp_documents
python -m app.cli.classify_pncp_opportunities
```

## Oportunidades

A classificação primeiro confirma o contexto de projetor em objeto, item ou
documento e descarta falsos positivos conhecidos. A avaliação técnica posterior
usa o perfil objetivo `projetores`, informa `perfil_versao` e mantém evidências
por requisito. Cada evidência documental inclui o número de controle PNCP,
URL/URI, SHA-256, datas de publicação, primeira coleta e análise, além da versão
do extrator. O relatório de adequação associa cada requisito aos trechos usados.

Por padrão, `GET /pncp/oportunidades` retorna a versão corrente do perfil. O
parâmetro `perfil_versao` permite consultar resultados históricos.

Cada execução informa sua própria identificação no resultado do comando de
classificação. O endpoint de histórico permite comparar reprocessamentos sem
alterar o contrato da listagem corrente.

## Limitações conhecidas

- busca em memória continua disponível por compatibilidade e filtra somente a
  página recebida da fonte;
- extração documental cobre texto, PDF e ZIP, mas documentos sem texto exigem
  análise humana ou OCR futuro;
- a classificação automática é apoio à triagem, não decisão de contratação.
