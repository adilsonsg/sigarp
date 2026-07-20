# Pesquisa de contratações no PNCP

## Endpoint do SIGARP

`POST /pncp/contratacoes/pesquisar`

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

## Limitação desta entrega

A Sprint 3A M2 consulta apenas uma página por requisição e não grava dados. Paginação automatizada e persistência ficam para as próximas entregas.
