# Checklist — Sprint 3A M2

- [ ] `/health` retorna `0.3.0-alpha2`.
- [ ] `/docs` exibe o grupo `PNCP`.
- [ ] `POST /pncp/contratacoes/pesquisar` responde sem erro.
- [ ] A consulta envia datas ao PNCP no formato `YYYYMMDD`.
- [ ] A UF é normalizada para letras maiúsculas.
- [ ] O filtro textual ignora acentos e diferença entre maiúsculas/minúsculas.
- [ ] `somente_srp=true` mantém apenas registros SRP da página consultada.
- [ ] Erros remotos são convertidos em HTTP 502, 503 ou 504.
- [ ] Todos os testes passam.
- [ ] Ruff, Black e isort passam.
