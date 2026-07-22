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
- PostgreSQL: validar antes da publicação da tag
- Configuração: ausência de identidades mantém comportamento fail-closed
