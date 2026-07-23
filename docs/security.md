# Segurança e controle de acesso

## Estado atual

A API usa autenticação Bearer fail-closed nas rotas de dados. `/health`, `/docs`,
`/redoc` e `/openapi.json` expõem apenas estado mínimo e metadados da API. O
backend recebe identidades por `AUTH_PRINCIPALS`, guarda apenas SHA-256 de tokens
fortes e compara hashes em tempo constante. Tokens em claro pertencem ao cliente
e devem ficar em cofre de segredos institucional.

Este adaptador é adequado para a implantação controlada da alpha. Uma integração
OIDC institucional poderá substituí-lo sem alterar as regras de autorização nem
os registros de auditoria.

## Papéis

| Papel | Permissões mínimas |
|---|---|
| `leitor` | consultas de órgãos, PNCP, oportunidades, execuções e históricos |
| `analista` | permissões de leitor e revisão humana de oportunidades |
| `administrador` | permissões de analista e funções administrativas |

Um token reconhecido sem papel autentica em `/auth/me`, mas recebe `403` nas
rotas protegidas. Token ausente ou inválido recebe `401` e
`WWW-Authenticate: Bearer`.

## Configuração

`AUTH_PRINCIPALS` é uma lista JSON em uma única linha:

```json
[
  {
    "subject": "pessoa@ifmt.edu.br",
    "name": "Pessoa Responsável",
    "role": "analista",
    "token_sha256": "<sha256-hexadecimal-com-64-caracteres>"
  }
]
```

Não grave o token em claro no JSON, `.env.example`, Git, logs, scripts ou
documentação. Em produção, injete a variável pelo gerenciador de segredos e
publique a API somente por HTTPS.

`POSTGRES_PASSWORD` também é obrigatório por ambiente e não possui valor padrão.
O Compose constrói `DATABASE_URL` em tempo de execução. Use senha hexadecimal
forte para evitar ambiguidades de codificação em URL.

## Rotação

1. gere um token aleatório novo com pelo menos 256 bits;
2. armazene o token em claro no cofre e adicione somente seu SHA-256 à lista;
3. reinicie o backend e valide `/auth/me` com o token novo;
4. atualize os consumidores;
5. remova o hash antigo e reinicie novamente;
6. registre responsável, motivo e horário da rotação.

## Auditoria de revisão

`PATCH /pncp/oportunidades/{assessment_id}/revisao` exige `analista` ou
`administrador`. Cada decisão cria um evento imutável com identidade, nome,
papel, justificativa, data, execução automática avaliada, snapshot do resultado e
valores anterior/novo. O estado corrente fica na avaliação; eventos anteriores
não são sobrescritos.

## Vulnerabilidades e cadeia de suprimentos

O canal de reporte, versões atendidas e metas iniciais estão em `SECURITY.md`.
Detalhes da varredura de segredos, auditoria de dependências, SBOM e checksums
estão em `docs/supply-chain.md`.

Falhas confirmadas de severidade alta ou crítica bloqueiam a integração. Qualquer
exceção precisa de responsável, justificativa, mitigação e prazo. Um segredo
detectado é tratado como comprometido: revogue ou rotacione primeiro e só depois
remova a exposição do código ou do histórico.

## Regras operacionais

- não registrar cabeçalho `Authorization`;
- não usar tokens em parâmetros de URL;
- não habilitar bypass de autenticação por ambiente;
- manter `/health` sem dados sensíveis;
- limitar acesso ao `.env` e aos backups;
- investigar repetição de `401` e `403` no gateway/reverse proxy;
- substituir imediatamente qualquer token exposto.
- manter Actions e dependências sob atualização e revisão automatizadas;
- anexar SBOM e checksums a cada release.
