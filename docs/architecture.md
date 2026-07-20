# Arquitetura do SIGARP

## Visão geral

O backend segue uma arquitetura em camadas:

```text
API
 ├─ valida entrada e saída
 ├─ traduz erros HTTP
 └─ injeta dependências
       |
       v
Services
 ├─ aplica regras de negócio
 └─ orquestra operações
       |
       v
Repositories
 ├─ executa persistência
 └─ isola SQLAlchemy
       |
       v
Models / PostgreSQL
```

## Diretórios

- `app/api`: rotas, dependências e handlers.
- `app/core`: configuração, logging e exceções.
- `app/database`: engine, sessões e base ORM.
- `app/models`: modelos SQLAlchemy.
- `app/repositories`: acesso a dados.
- `app/schemas`: contratos Pydantic.
- `app/services`: regras e casos de uso.
- `tests`: testes automatizados.

## Princípios

- API-first.
- Dados oficiais preservados.
- Separação entre dado bruto e normalizado.
- Neutralidade na comparação.
- Rastreabilidade.
- Migrations obrigatórias.
- Configuração por variáveis de ambiente.

## Inicialização

`create_app()` monta a aplicação, registra rotas, middleware e handlers.
Isso permite testar e evoluir a inicialização sem concentrar tudo em `main.py`.
