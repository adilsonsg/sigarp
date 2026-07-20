# Changelog

Todas as mudanças relevantes do SIGARP serão registradas neste arquivo.

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
