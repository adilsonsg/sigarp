# ADR-007 — Autenticação e revisão humana auditável

- Status: aceito
- Data: 2026-07-22
- Decisão aplicável desde: `0.7.0-alpha1`

## Contexto

A API possuía consultas e cadastro de órgãos sem identidade. A evolução para
revisão humana e futura integração institucional exige atribuir cada mudança a
uma pessoa, aplicar privilégio mínimo e impedir que segredos entrem no código ou
nos logs.

## Decisão

- somente health check e metadados OpenAPI permanecem públicos;
- tokens Bearer fortes são apresentados pelo cliente, mas o backend recebe e
  mantém somente seus hashes SHA-256 por configuração de ambiente;
- a autorização usa a hierarquia `leitor < analista < administrador`;
- configuração vazia falha fechada;
- decisões humanas são eventos append-only com autor, papel, justificativa,
  data, execução automática, resultado avaliado e valores anterior/novo;
- exclusões que removeriam a trilha de revisão são restringidas pelo banco;
- autenticação fica isolada em adaptador para futura troca por OIDC/SUAP.

## Alternativas consideradas

- senhas locais: rejeitadas por ampliar armazenamento de credenciais e processos
  de recuperação;
- cabeçalhos de identidade sem assinatura: rejeitados porque podem ser forjados
  quando a aplicação é acessada fora de um proxy confiável;
- bypass em desenvolvimento: rejeitado porque mascara falhas de autorização.

## Consequências

- consumidores devem enviar Bearer token em toda rota protegida;
- tokens precisam de geração, cofre, distribuição e rotação operacional;
- hashes não protegem tokens fracos, portanto a entropia mínima é obrigatória;
- OIDC continua recomendado para implantação institucional em escala;
- a revisão humana passa a ser distinguível da classificação automática.
