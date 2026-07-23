# Inventário preliminar de dados e tratamento

## Escopo

Este inventário apoia a avaliação institucional do SIGARP. Ele descreve o
tratamento implementado, mas não define por conta própria a base legal, o prazo de
retenção, o controlador, o operador ou o encarregado. Essas decisões dependem de
aprovação formal do IFMT.

## Categorias

| Conjunto | Fonte | Exemplos | Finalidade técnica | Acesso atual | Retenção |
|---|---|---|---|---|---|
| Contratações públicas | API pública do PNCP | órgão, objeto, datas, valores, identificador e URL | localizar e organizar oportunidades públicas | papéis `leitor`, `analista` e `administrador` | pendente de aprovação |
| Itens da contratação | API pública do PNCP | descrição, quantidade, unidade e valor | classificação e avaliação técnica | papéis autorizados | pendente de aprovação |
| Documentos públicos | PNCP e anexos oficiais | edital, termo de referência e texto extraído | produzir evidência verificável | papéis autorizados | pendente de aprovação |
| Avaliações automáticas | dados derivados | classificação, pontuação, evidências e versões | priorizar análise sem decisão final automática | papéis autorizados | vinculado à política de auditoria, a aprovar |
| Identidades de acesso | configuração institucional | identificador, nome, papel e hash do token | autenticar e autorizar | administração operacional | enquanto o acesso estiver vigente, sujeito a política |
| Revisões humanas | usuários autenticados | autor, papel, decisão, justificativa e data | responsabilização e auditoria | papéis autorizados | pendente de aprovação |
| Logs técnicos | aplicação e infraestrutura | horário, rota, status e `request_id` | segurança, diagnóstico e operação | equipe operacional | pendente de aprovação |

## Possíveis dados pessoais

Embora as fontes sejam públicas, documentos e metadados podem conter nomes,
cargos, assinaturas, contatos profissionais, identificadores e, eventualmente,
outros dados pessoais. Publicidade da fonte não elimina os princípios de
finalidade, necessidade, transparência, segurança e prevenção.

O SIGARP deve:

- coletar somente campos e documentos necessários à finalidade aprovada;
- não usar dados pessoais para pontuação técnica;
- não registrar tokens, senhas ou cabeçalhos `Authorization`;
- restringir consultas por identidade e papel;
- preservar origem, versão e histórico para explicabilidade;
- permitir descarte controlado quando a política institucional determinar;
- manter decisão administrativa sob responsabilidade humana.

## Fluxos e destinatários

O fluxo implementado é PNCP → coleta → PostgreSQL → extração → avaliação
versionada → API → revisão humana. Não há, nesta etapa, envio ao SUAP nem
compartilhamento com terceiros. Uma integração futura exige inventário e
aprovação específicos antes da ativação.

O acesso local é destinado a agentes institucionais autorizados. A exposição
pública da API de dados não está aprovada; somente `/health` e metadados OpenAPI
permanecem públicos na configuração atual.

## Decisões institucionais necessárias

Antes de produção, o responsável institucional deve registrar:

1. finalidade pública específica de cada operação;
2. hipótese legal aplicável e sua justificativa;
3. controlador, eventual operador e encarregado;
4. categorias necessárias e campos a excluir ou mascarar;
5. prazos de retenção, arquivamento e eliminação;
6. destinatários e condições de compartilhamento;
7. canal para titulares e tratamento de incidentes;
8. necessidade de relatório de impacto ou outra avaliação.

O acompanhamento dessas decisões está em
`docs/compliance/institutional-decisions.md`.

## Referências oficiais

- [Lei nº 13.709/2018 — LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm);
- [Guia orientativo da ANPD sobre tratamento de dados pessoais pelo Poder Público](https://www.gov.br/saude/pt-br/acesso-a-informacao/lgpd/publicacoes/guia-orientativo-tratamento-de-dados-pessoais-pelo-poder-publico);
- [Guia da ANPD sobre agentes de tratamento e encarregado](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-para-definicoes-dos-agentes-de-tratamento-de-dados-pessoais-e-do-encarregado).
