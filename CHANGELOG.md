# Changelog

Todas as mudanças relevantes do SIGARP serão registradas neste arquivo.

## [0.9.0-alpha1] - 2026-07-23

### Adicionado

- prefixo canônico `/api/v1` para a API pública;
- paginação padronizada com `items`, `page`, `page_size`, `total` e
  `total_pages` nas coleções locais;
- contrato único de erros com `detail`, `code`, `request_id` e detalhes de
  validação;
- testes de contrato OpenAPI, compatibilidade, paginação e correlação de erros;
- política explícita de compatibilidade e depreciação da API.

### Compatibilidade

- rotas sem prefixo continuam funcionais durante a transição;
- rotas legadas de dados aparecem como depreciadas no OpenAPI;
- nenhuma migration de banco foi adicionada; o head permanece
  `20260722_0010`.

### Validado

- 78 testes automatizados aprovados;
- Ruff, Black, isort e compilação Python aprovados.

## [0.8.0-alpha1] - 2026-07-23

### Adicionado

- workflow contínuo com Gitleaks, `pip-audit` e Dependency Review;
- Dependabot semanal para dependências Python e GitHub Actions;
- geração automática de pacote da tag, SBOM SPDX JSON e checksums SHA-256;
- política privada de reporte e tratamento de vulnerabilidades;
- inventário preliminar de dados e registro de decisões institucionais pendentes;
- guias de instalação, validação e cadeia de suprimentos da versão.

### Alterado

- GitHub Actions oficiais atualizadas para versões baseadas em Node 24;
- checkout de CI sem persistência de credenciais e com permissões mínimas;
- FastAPI, Starlette, Pytest, pytest-asyncio, pytest-cov e Black atualizados para
  versões sem os alertas encontrados pela auditoria;
- baseline da aplicação atualizada para `0.8.0-alpha1`.

### Conformidade

- licença, base legal, agentes de tratamento, retenção e homologação de produção
  permanecem explicitamente sujeitos à aprovação formal do IFMT;
- nenhuma hipótese legal ou autorização de distribuição foi presumida pelo
  projeto.

## [0.7.0-alpha1] - 2026-07-22

### Adicionado

- autenticação Bearer fail-closed com configuração contendo somente SHA-256 de
  tokens fortes;
- papéis hierárquicos `leitor`, `analista` e `administrador`;
- endpoint `GET /auth/me` para consulta da identidade autenticada;
- revisão humana com autor, papel, justificativa, data e valores anterior/novo;
- histórico imutável de revisões e migração Alembic `20260722_0010`;
- ADR e guia operacional de segurança e rotação de tokens.

### Alterado

- consultas exigem papel leitor, revisão exige analista e cadastro de órgãos
  exige administrador;
- versão da aplicação para `0.7.0-alpha1`.

### Segurança

- tokens em claro não são persistidos nem incluídos em logs;
- configuração vazia nega todas as rotas de dados protegidas; apenas health
  check e metadados OpenAPI permanecem públicos.
- senha de PostgreSQL removida do repositório e exigida por variável de ambiente.

### Validado

- migração `20260722_0010` aprovada em PostgreSQL 16.14;
- 72 testes automatizados e verificações Ruff, Black e isort aprovados;
- matriz com nove cenários de autenticação e autorização aprovada;
- duas revisões sucessivas confirmaram autoria, transição de estado, vínculo com
  a execução automática e preservação imutável do primeiro evento.

## [0.6.0-alpha1] - 2026-07-22

### Adicionado

- registro de cada execução de classificação, incluindo parâmetros, status,
  estatísticas, versão do perfil e versão do analisador;
- snapshots imutáveis das avaliações para cada reprocessamento;
- endpoints de consulta de execuções e histórico por avaliação;
- SHA-256 e datas de origem/análise na cadeia de evidência documental;
- versão do extrator, data da primeira coleta e relatório por requisito com
  trechos de origem;
- migração Alembic `20260722_0009` e ADR de rastreabilidade.

### Alterado

- avaliações correntes passam a apontar para a última execução responsável;
- comando de classificação informa `execucao_id` e `status_execucao`;
- versão da aplicação para `0.6.0-alpha1`.

## [0.5.0-alpha6] - 2026-07-22

### Adicionado

- Perfil objetivo de projetores em arquivo JSON externo, validado e versionado.
- Persistência de `perfil_versao` para manter o histórico das avaliações.
- Migração Alembic `20260722_0008` com identificação explícita das avaliações
  legadas da alpha5.
- Teste de regressão que assegura resultado idêntico para fabricantes distintos
  quando as especificações técnicas são equivalentes.

### Alterado

- Avaliação técnica passa a considerar somente requisitos objetivos habilitados
  no perfil.
- Consulta de oportunidades seleciona, por padrão, a versão corrente do perfil.
- API de oportunidades informa e permite filtrar `perfil_versao`.
- Contêiner do backend respeita comandos informados ao `docker compose run`,
  permitindo executar testes, lint e tarefas administrativas.
- Imagem do backend inclui a configuração de Black, isort e Ruff compatível com
  seu contexto de build isolado.

### Removido

- Preferência, observação e campo de avaliação associados a marca ou família
  comercial específica.

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
