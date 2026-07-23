# Contribuição

## Fluxo

1. Atualize a branch `main`.
2. Crie uma branch `feature/...`, `fix/...` ou `docs/...`.
3. Faça alterações pequenas e testáveis.
4. Execute qualidade e testes.
5. Faça commit descritivo.
6. Abra pull request.

## Padrão de commits

Exemplos:

```text
feat: adiciona coletor PNCP
fix: corrige validação de CNPJ
chore: atualiza dependências
docs: documenta arquitetura
test: amplia cobertura da API de órgãos
```

## Antes do commit

```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
docker compose run --rm backend pytest -v
```

O GitHub também executa Gitleaks, `pip-audit` e Dependency Review. Antes de abrir
o pull request, confira que nenhum segredo, `.env`, banco ou backup entrou no
diff:

```bash
git status --short
git diff --check
git diff --cached
```

## Regras

- Não incluir segredos.
- Não editar migrations já publicadas.
- Não acessar banco diretamente nas rotas.
- Não remover rastreabilidade de dados oficiais.
- Não suprimir alerta de segurança sem exceção documentada, responsável e prazo.
- Não escolher licença ou base legal em nome da instituição.
- Não editar artefatos de release manualmente depois da geração automatizada.
