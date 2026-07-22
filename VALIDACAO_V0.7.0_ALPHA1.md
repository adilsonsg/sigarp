# Validação — SIGARP v0.7.0-alpha1

## Critérios de aceite

| Controle | Evidência esperada |
|---|---|
| Versão | `/health` retorna `0.7.0-alpha1` |
| Banco | head `20260722_0010` |
| Fail-closed | rota protegida sem token retorna `401` |
| Identidade | `/auth/me` retorna sujeito, nome e papel |
| Leitor | consulta permitida; mutações negadas |
| Analista | revisão permitida; administração negada |
| Administrador | administração e revisão permitidas |
| Sem papel | identidade reconhecida, acesso protegido negado |
| Auditoria | revisão registra autor, justificativa, data e antes/depois |
| Imutabilidade | segunda revisão mantém o primeiro evento |
| Segredos | configuração e logs não contêm token em claro |
| Qualidade | Pytest, Ruff, Black e isort aprovados |

## Resultado no ambiente de desenvolvimento

- Testes automatizados: 72 aprovados
- Migração: `0009 → 0010 → 0009 → 0010` validada em SQLite
- PostgreSQL 16.14: migração `0009 → 0010` aprovada com DDL transacional
- Configuração: ausência de identidades mantém comportamento fail-closed
- Qualidade: Ruff, Black e isort aprovados; 115 arquivos sem alteração pelo Black

## Validação PostgreSQL e API

Validação executada em 22/07/2026, após backup custom-format confirmado com
`pg_restore -l` e rotação da senha do papel `sigarp`:

- Alembic confirmou `20260722_0009` antes da atualização e
  `20260722_0010 (head)` depois dela;
- `pncp_opportunity_assessments` recebeu `revisao_status`, `revisado_por` e
  `revisado_em` como campos anuláveis, preservando registros legados;
- `pncp_opportunity_reviews` foi criada com duas chaves estrangeiras
  `ON DELETE RESTRICT`, para avaliação e execução de processamento;
- `/health` respondeu `0.7.0-alpha1` e `online`;
- matriz de autenticação e autorização obteve 9 de 9 resultados esperados;
- token ausente ou inválido retornou `401`;
- identidade sem papel autenticou em `/auth/me` e recebeu `403` em dados;
- leitor consultou dados, mas recebeu `403` em administração e revisão;
- analista revisou oportunidade, mas recebeu `403` em administração;
- administrador acessou consulta e revisão;
- `.env` permaneceu ignorado e fora do índice do Git.

## Evidência de revisão imutável

A avaliação `402`, referente ao número de controle PNCP
`04264173000178-1-000054/2026`, foi usada na validação:

| Evento | Ator | Papel | Decisão | Estado anterior | Execução |
|---|---|---|---|---|---:|
| 1 | `analyst-local` | `analista` | `EXIGE_ANALISE_ADICIONAL` | sem revisão | 3 |
| 2 | `admin-local` | `administrador` | `APROVADA` | `EXIGE_ANALISE_ADICIONAL` | 3 |

Os dois eventos mantiveram IDs distintos, justificativas, datas, valores
anterior/novo e snapshot da classificação automática
`CONFIRMADA_DOCUMENTO`, perfil `1.0.0` e analisador `1.0.0`. Após a segunda
revisão, o primeiro evento continuou consultável sem alteração, enquanto o
estado corrente passou a `APROVADA`, revisado por `admin-local`.

Resultado: controles de acesso, persistência PostgreSQL, auditoria e
imutabilidade aprovados para publicação da tag `v0.7.0-alpha1`.
