# Política de segurança

## Versões com suporte

Enquanto o SIGARP estiver em fase alpha, somente a pré-release mais recente
publicada recebe correções de segurança. Versões anteriores devem ser atualizadas
antes da implantação institucional.

## Reporte responsável

Não abra issue pública com detalhes de uma vulnerabilidade, credencial, token,
arquivo `.env`, backup ou dado pessoal.

Use **Security > Advisories > Report a vulnerability** no repositório GitHub para
enviar o relato privadamente. Inclua, quando possível:

- versão e commit afetados;
- impacto observado;
- passos mínimos para reprodução;
- evidências sem credenciais ou dados pessoais;
- mitigação sugerida.

Se o reporte privado não estiver habilitado, contate o responsável pelo
repositório pedindo um canal institucional seguro e aguarde a confirmação antes
de transmitir detalhes sensíveis.

## Tratamento

Metas iniciais, sujeitas à aprovação operacional do IFMT:

| Severidade estimada | Triagem | Plano de contenção/correção |
|---|---:|---:|
| crítica | 1 dia útil | 2 dias úteis |
| alta | 2 dias úteis | 5 dias úteis |
| média | 5 dias úteis | 15 dias úteis |
| baixa | 10 dias úteis | próximo ciclo planejado |

O projeto confirmará o recebimento, avaliará impacto e versões afetadas,
coordenará a correção e publicará orientação quando a divulgação não aumentar o
risco. Os prazos são objetivos de resposta, não garantia de resolução.

Segredos expostos devem ser revogados ou rotacionados imediatamente. O histórico
Git não é um cofre e remover um valor de um commit não invalida a credencial.
