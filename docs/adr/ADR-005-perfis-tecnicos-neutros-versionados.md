# ADR-005 — Perfis técnicos neutros e versionados

- Status: aceito
- Data: 2026-07-22
- Decisão aplicável desde: `0.5.0-alpha6`

## Contexto

A avaliação de oportunidades precisa ser explicável, reproduzível e isonômica.
O perfil anterior continha preferência explícita por uma família comercial. Esse
critério não era requisito técnico e poderia alterar a interpretação da análise.
Além disso, a versão do conjunto de critérios não era persistida, impedindo a
reprodução histórica de uma classificação.

## Decisão

Os perfis de avaliação serão arquivos externos, imutáveis por versão e compostos
somente por requisitos técnicos objetivos. Cada avaliação persistirá o par
`perfil` e `perfil_versao`.

O perfil corrente de projetores é `projectors_v1.json`, versão `1.0.0`. Alterações
de critérios exigem um novo arquivo e incremento SemVer. Marcas, fabricantes,
modelos e famílias comerciais podem existir como evidência documental, mas não
podem integrar requisito, peso, pontuação ou regra de classificação.

Avaliações anteriores à decisão são migradas como `legacy-alpha5`. A API consulta
por padrão a versão corrente e aceita filtro explícito para o histórico.

## Consequências

- uma avaliação pode ser reproduzida com a versão exata do perfil;
- critérios podem evoluir sem sobrescrever resultados históricos;
- testes devem provar equivalência entre fabricantes para especificações iguais;
- o perfil precisa ser validado na inicialização e revisado como código;
- uma mudança de versão exige reclassificação deliberada das oportunidades.

## Controles

- revisão obrigatória do arquivo de perfil;
- teste de regressão de neutralidade;
- restrição única por contratação, perfil e versão;
- exposição de `perfil_versao` na API;
- ausência de termos comerciais no arquivo de critérios.
