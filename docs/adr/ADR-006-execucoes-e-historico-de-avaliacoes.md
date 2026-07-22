# ADR-006 — Execuções e histórico de avaliações

- Status: aceito
- Data: 2026-07-22
- Decisão aplicável desde: `0.6.0-alpha1`

## Contexto

A alpha6 preserva avaliações por versão de perfil, mas um novo processamento com
o mesmo perfil atualiza o registro existente. Isso atende à consulta operacional,
porém não permite reconstruir qual execução produziu cada resultado nem comparar
reprocessamentos feitos com versões diferentes do analisador.

## Decisão

Manteremos duas representações complementares:

- `pncp_opportunity_assessments` contém o estado corrente, otimizado para busca;
- `pncp_opportunity_assessment_history` contém um snapshot imutável por
  contratação, perfil, versão e execução;
- `pncp_processing_runs` registra início, conclusão, parâmetros, estatísticas,
  erro, versão do perfil e versão do analisador.

Cada classificação em lote cria uma execução antes de processar contratações. O
registro corrente aponta para `ultima_execucao_id`, e o mesmo payload é persistido
como snapshot histórico. Reprocessar não remove snapshots anteriores.

A cadeia de evidência documental inclui identificador PNCP, URL/URI, SHA-256 do
conteúdo, data de publicação, data da primeira coleta, instante de análise e
versão do extrator. O relatório associa cada requisito ao resultado e aos trechos
de origem. Registros existentes recebem `analisador_versao=legacy-unknown`, e
documentos já analisados recebem `extrator_versao=legacy-unknown`, até serem
reprocessados.

## Consequências

- resultados podem ser reconstruídos e comparados por execução;
- a API corrente permanece compatível e rápida;
- o volume histórico cresce a cada reprocessamento;
- exclusões de execução são restringidas enquanto houver histórico relacionado;
- políticas institucionais de retenção podem arquivar snapshots, mas não devem
  sobrescrevê-los silenciosamente.

## Retenção

Até aprovação de política institucional específica, execuções e snapshots não
serão removidos automaticamente. Documentos seguem a política da fonte e os
requisitos legais aplicáveis; qualquer descarte futuro deverá registrar autor,
regra, data, intervalo afetado e checksum do lote exportado.
