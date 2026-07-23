# Registro de decisões institucionais pendentes

## Regra

Os controles técnicos podem evoluir sem atribuir ao software decisões jurídicas
ou administrativas. Os itens abaixo precisam de responsável nominal, evidência
de aprovação e data de revisão antes de produção.

| ID | Decisão | Responsável esperado | Estado | Evidência |
|---|---|---|---|---|
| INST-01 | titularidade do código e licença de distribuição | gestão do projeto e área jurídica | PENDENTE | ata, despacho ou processo |
| INST-02 | finalidade pública específica do tratamento | área demandante | PENDENTE | termo de abertura ou ato equivalente |
| INST-03 | hipótese legal por operação de tratamento | jurídico/encarregado | PENDENTE | parecer ou registro formal |
| INST-04 | identificação de controlador, operador e encarregado | alta administração/encarregado | PENDENTE | ato institucional |
| INST-05 | retenção, arquivamento e descarte | gestão documental e encarregado | PENDENTE | tabela e procedimento aprovados |
| INST-06 | destinatários e eventual integração SUAP | donos dos sistemas | PENDENTE | acordo e contrato de integração |
| INST-07 | exposição de rede e ambiente de produção | segurança e infraestrutura | PENDENTE | homologação técnica |
| INST-08 | canal e metas de resposta a incidentes | segurança e gestão do projeto | PENDENTE | procedimento aprovado |

## Licença

Nenhum arquivo `LICENSE` é adicionado até que a titularidade e a licença sejam
formalmente aprovadas. A ausência de licença não deve ser interpretada como
autorização de uso, cópia, modificação ou redistribuição.

Após a decisão, registrar:

- nome e identificador SPDX da licença;
- titular ou titulares;
- eventual autorização institucional;
- data e processo de aprovação;
- impacto sobre dependências e distribuição.

## Proteção de dados

Não se presume que uma única hipótese legal cubra todos os fluxos. A decisão deve
relacionar finalidade, categorias de dados, operação, hipótese legal,
destinatários, retenção e salvaguardas.

O inventário inicial está em `docs/compliance/data-inventory.md`. Qualquer nova
fonte, integração, endpoint público ou uso analítico deve atualizar o inventário
antes da implantação.

## Critério para produção

A implantação de produção só pode ser marcada como aprovada quando INST-01 a
INST-08 tiverem decisão ou dispensa formal, e quando a evidência estiver
referenciada neste documento sem incluir dados pessoais ou segredos.
