# Changelog

Todas as mudanças relevantes do SIGARP serão registradas neste arquivo.

## [0.3.0-alpha2-fix1] - 2026-07-20

### Corrigido

- Centralização de timeout, retry, backoff, pool e logging em `BaseHttpClient`.
- `PNCPClient` refatorado para reutilizar a infraestrutura HTTP comum.
- Versão do `docker-compose.yml` e do `.env` alinhada com `0.3.0-alpha2`.
- Testes unitários adicionados para o cliente HTTP reutilizável.

## [0.3.0-alpha2] - 2026-07-20

### Adicionado

- Endpoint `POST /pncp/contratacoes/pesquisar`.
- Schemas Pydantic para páginas e contratações do PNCP.
- Parser tolerante a campos adicionais da fonte oficial.
- Filtro textual local sem diferenciação de acentos.
- Filtro local para registros de preços (`srp`).
- Tratamento HTTP para timeout, limite de requisições e falhas remotas.
- Testes do parser, serviço e endpoint REST.

### Alterado

- Versão da aplicação para `0.3.0-alpha2`.

## [0.3.0-alpha1] - 2026-07-20

### Adicionado

- Arquitetura base de coletores com contrato abstrato e registry.
- Cliente HTTP assíncrono para a API oficial PNCP Consulta.
- Retry com backoff exponencial para HTTP 429 e erros transitórios 5xx.
- Tratamento específico de timeout, rate limit e respostas remotas.
- Configuração PNCP por variáveis de ambiente.
- Testes unitários do registry e do cliente PNCP.
- Documentação da arquitetura de coletores.

### Alterado

- Versão da aplicação para `0.3.0-alpha1`.
- Logging estruturado passa a registrar a tentativa do coletor.

## [0.2.1] - 2026-07-20

### Adicionado

- Logging estruturado em JSON.
- Middleware de identificação de requisições.
- Tratamento global de exceções.
- Configuração centralizada de ambiente e logging.
- Pipeline de integração contínua com GitHub Actions.
- Configuração unificada de Ruff, Black, isort e Pytest.
- Scripts auxiliares para Windows e Linux.
- Documentação de arquitetura, banco e contribuição.
- Testes para tratamento de erros e cabeçalho de requisição.

### Alterado

- Versão da aplicação para `0.2.1`.
- Docker Compose com políticas de reinício e healthcheck do backend.
- Organização da inicialização da aplicação por meio de uma fábrica.

### Mantido

- API de órgãos.
- SQLAlchemy 2.
- Alembic.
- PostgreSQL.

## 0.4.0-alpha1 - 2026-07-20

- Adiciona o método tipado `PNCPClient.buscar_contratacoes_publicadas`.
- Refatora `PNCPSearchService` para usar a interface de domínio do cliente PNCP.
- Adiciona `GET /pncp/search` com filtros por termo, período, modalidade, UF, página e SRP.
- Mantém compatibilidade com `POST /pncp/contratacoes/pesquisar`.
- Amplia os testes do cliente, serviço e API PNCP.

## [0.4.0-alpha3] - 2026-07-20

### Adicionado
- sincronização paginada de contratações publicadas no PNCP;
- persistência local em `pncp_contractings` com UPSERT;
- filtro padrão para contratações SRP;
- estatísticas de leitura, inserção, atualização, descarte e erro;
- comando `python -m app.cli.sync_pncp`;
- migração Alembic `20260720_0003`;
- testes de paginação e idempotência da sincronização.
