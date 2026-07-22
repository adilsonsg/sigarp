# Backlog executável — Etapa 0

Itens prontos para criação como issues. Prioridade P0 significa bloqueio para uma
implantação institucional; P1 deve entrar no ciclo imediatamente seguinte.

## P0-01 — Publicar baseline reproduzível da alpha6

- Labels sugeridos: `P0`, `release`, `devops`
- Dependências: nenhuma
- Estado: implementado localmente; aguarda revisão e publicação

### Objetivo

Convergir a baseline funcional da alpha5 com o repositório principal e publicar a
alpha6 com migração, instruções, changelog e evidências de validação.

### Critérios de aceite

- branch revisada e integrada ao `main`;
- tag assinada `v0.5.0-alpha6` criada a partir do commit de integração;
- `alembic heads` retorna apenas `20260722_0008`;
- instalação limpa e atualização desde alpha5 são validadas;
- suíte, lint e formatação passam no CI;
- pacote ou imagem possui checksum publicado.

## P0-02 — Garantir neutralidade dos perfis técnicos

- Labels sugeridos: `P0`, `compliance`, `domain`
- Dependências: P0-01
- Estado: implementado na alpha6

### Objetivo

Impedir que marca, fabricante, fornecedor, modelo ou família comercial influencie
pontuação e classificação técnica.

### Critérios de aceite

- perfil externo contém somente critérios objetivos;
- cada avaliação registra a versão do perfil;
- avaliações legadas são distinguíveis das atuais;
- fabricantes diferentes com especificações iguais produzem resultados iguais;
- revisão automatizada bloqueia termos comerciais em arquivos de perfil.

## P0-03 — Completar rastreabilidade e trilha de auditoria

- Labels sugeridos: `P0`, `audit`, `data`
- Dependências: P0-02
- Estado: concluído tecnicamente na `0.6.0-alpha1`; validação PostgreSQL aprovada

### Objetivo

Permitir reconstruir cada resultado a partir da fonte, documento, extrator, perfil
e instante de processamento.

### Critérios de aceite

- evidência registra URL/URI, SHA-256, data de coleta e identificador PNCP;
- avaliação registra versão do extrator e do perfil;
- reprocessamento cria nova execução sem apagar a anterior;
- relatório explica requisito por requisito com trecho de origem;
- retenção e descarte de documentos são documentados.

## P0-04 — Definir controles de acesso antes de funções mutáveis

- Labels sugeridos: `P0`, `security`, `api`
- Dependências: P0-01
- Estado: pendente

### Objetivo

Adicionar autenticação institucional e autorização por função antes de expor
administração, revisão humana ou integração SUAP.

### Critérios de aceite

- papéis mínimos `leitor`, `analista` e `administrador` definidos;
- endpoints mutáveis exigem identidade e papel adequado;
- decisões humanas registram autor, data, justificativa e valores anterior/novo;
- segredos não ficam no repositório nem em logs;
- testes cobrem acesso permitido, negado e usuário sem papel.

## P0-05 — Estabelecer segurança e conformidade da entrega

- Labels sugeridos: `P0`, `security`, `legal`
- Dependências: P0-01
- Estado: pendente

### Objetivo

Formalizar licença, tratamento de dados, cadeia de dependências e resposta a
vulnerabilidades.

### Critérios de aceite

- titular do projeto aprova e adiciona `LICENSE`;
- inventário de dados e base legal são aprovados pelo responsável institucional;
- CI executa varredura de segredos e dependências;
- SBOM e checksums acompanham cada release;
- política de reporte e correção de vulnerabilidades é publicada.

## P1-01 — Contratos estáveis e paginação da API

- Labels sugeridos: `P1`, `api`, `architecture`
- Dependências: P0-03
- Estado: pendente

### Critérios de aceite

- API pública possui prefixo de versão;
- listas retornam paginação e total sem limites silenciosos;
- erros seguem contrato único com `request_id`;
- OpenAPI é verificado por teste de contrato;
- mudanças incompatíveis possuem política de depreciação.

## P1-02 — Preparar adaptador SUAP desacoplado

- Labels sugeridos: `P1`, `integration`, `suap`
- Dependências: P0-03, P0-04
- Estado: pendente

### Critérios de aceite

- porta de integração independe de protocolo e credenciais concretas;
- envio usa idempotência, fila persistente e retentativa controlada;
- falhas não interrompem ingestão ou busca;
- payloads, homologação e responsabilidade operacional são acordados com o IFMT;
- contrato e simulador são testados sem acesso ao SUAP real.
