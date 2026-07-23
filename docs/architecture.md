# Arquitetura do SIGARP

## Visão geral

O backend é um monólito modular em camadas. A ingestão preserva os dados oficiais;
a classificação e a avaliação técnica são etapas separadas e reprocessáveis.

```mermaid
flowchart TD
    PNCP["PNCP oficial"] --> COL["Coletores e sincronização"]
    COL --> RAW["Dados e documentos de origem"]
    RAW --> EXT["Extração e estruturação"]
    EXT --> CLS["Classificação de oportunidade"]
    CLS --> PRF["Perfil técnico versionado"]
    PRF --> AUD["Execução e snapshot histórico"]
    AUD --> API["API FastAPI /api/v1"]
    ID["Identidade configurada"] --> AUTH["Autenticação e papéis"]
    AUTH --> API
    API --> REV["Revisão humana auditável"]
    CI["CI: testes, segredos e dependências"] --> REL["Release: pacote, SBOM e SHA-256"]
    REL --> API
```

A API valida contratos e traduz erros; serviços orquestram casos de uso;
repositórios isolam a persistência; modelos SQLAlchemy representam o PostgreSQL.

## Diretórios

- `app/api`: rotas, dependências e handlers.
- `app/clients` e `app/collectors`: acesso resiliente às fontes oficiais.
- `app/core`: configuração, logging e exceções.
- `app/database`: engine, sessões e base ORM.
- `app/models`: modelos SQLAlchemy.
- `app/repositories`: acesso a dados.
- `app/schemas`: contratos Pydantic.
- `app/services`: regras e casos de uso.
- `app/sync`: ingestão idempotente de contratações, itens e documentos.
- `app/profiles`: critérios técnicos objetivos e versionados.
- `tests`: testes automatizados.

## Princípios

- API-first.
- Contratos públicos versionados e compatibilidade explícita.
- Dados oficiais preservados.
- Separação entre dado bruto e normalizado.
- Neutralidade na comparação.
- Rastreabilidade.
- Perfis imutáveis por versão.
- Classificação automatizada não substitui decisão humana.
- Autenticação fail-closed e privilégio mínimo.
- Migrations obrigatórias.
- Configuração por variáveis de ambiente.
- Privilégio mínimo no CI e artefatos produzidos a partir de tags.
- Conformidade depende de decisões institucionais explícitas, não de suposições
  do software.

## Inicialização

`create_app()` monta a aplicação, registra rotas, middleware e handlers.
Isso permite testar e evoluir a inicialização sem concentrar tudo em `main.py`.

A API canônica usa `/api/v1`. Coleções locais compartilham o envelope
`items`, `page`, `page_size`, `total` e `total_pages`; erros compartilham
`detail`, `code`, `request_id` e `errors`. Rotas anteriores sem versão seguem
ativas apenas como camada de compatibilidade e são marcadas como depreciadas no
OpenAPI.

## Limites dos módulos

- coletores não aplicam pontuação técnica;
- extração não decide adequação;
- perfis não contêm marca, fabricante, fornecedor ou família comercial;
- avaliações registram a versão do perfil;
- extrações e reprocessamentos registram as versões do extrator e do analisador;
- o estado corrente não substitui snapshots históricos;
- autenticação não conhece regras de domínio e autorização não recebe tokens em
  claro além do instante de verificação;
- revisões humanas são eventos imutáveis separados da classificação automática;
- uma futura integração SUAP deve usar adaptador próprio, idempotência e fila
  persistente, sem acoplamento ao domínio de busca.
- workflows de CI não recebem segredos de aplicação e usam permissões mínimas;
- releases são reconstruídas da árvore da tag e acompanhadas por SBOM e SHA-256;
- base legal, retenção, licença e aprovação de produção ficam fora do domínio e
  exigem registro institucional.

## Decisões

As decisões arquiteturais estão em `docs/adr`. O ADR-005 torna obrigatórios os
perfis neutros e versionados; o ADR-006 define a trilha de execução e histórico;
o ADR-007 estabelece autenticação, papéis e revisão humana auditável.

Os controles operacionais da cadeia de suprimentos estão em
`docs/supply-chain.md`; o inventário e as decisões institucionais pendentes estão
em `docs/compliance/`. A política de contrato e depreciação está em
`docs/api-versioning.md`.
