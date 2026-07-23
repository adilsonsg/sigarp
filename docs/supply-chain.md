# Segurança da cadeia de suprimentos

## Objetivo

Estabelecer controles reproduzíveis para código, dependências e artefatos de
release. Esses controles complementam revisão humana; não substituem a análise de
impacto de uma vulnerabilidade.

## Controles automatizados

### Integração contínua

`.github/workflows/backend-ci.yml` executa lint, formatação, testes e build da
imagem. As ações recebem apenas permissão de leitura e o checkout não mantém
credenciais no diretório de trabalho.

### Segurança contínua

`.github/workflows/security.yml` executa em pushes, pull requests, agenda semanal
e acionamento manual:

- Gitleaks no histórico disponível para detectar segredos;
- `pip-audit` sobre `backend/requirements.txt`;
- Dependency Review em pull requests, bloqueando novas vulnerabilidades de
  severidade alta ou crítica.

Um alerta confirmado bloqueia a integração até correção, atualização da
dependência ou exceção formal, temporária e justificada. Exceções devem registrar
responsável, impacto, mitigação, prazo e issue de acompanhamento.

### Atualizações

`.github/dependabot.yml` propõe atualizações semanais para dependências Python e
GitHub Actions. A atualização só deve ser integrada depois de CI aprovado e
revisão das notas da versão.

## Artefatos de release

Ao publicar uma GitHub Release, `.github/workflows/release-artifacts.yml`:

1. confirma que o checkout corresponde à tag;
2. gera o ZIP diretamente da árvore Git versionada;
3. gera SBOM no formato SPDX JSON;
4. calcula SHA-256 do ZIP e da SBOM;
5. anexa os três arquivos à release.

O workflow também pode ser executado manualmente para uma release já existente.
O nome esperado é:

```text
SIGARP-<versão>-release.zip
SIGARP-v<versão>-sbom.spdx.json
SHA256SUMS-v<versão>.txt
```

O pacote não inclui arquivos ignorados, `.env`, tokens, bancos ou backups porque
é produzido por `git archive` a partir do commit da tag.

## Validação local

```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
docker compose run --rm backend pytest -q
```

Antes da publicação, confirme que a tag aponta para o commit pretendido:

```bash
git rev-parse HEAD
git rev-parse 'vX.Y.Z^{}'
git diff --check origin/main..HEAD
```

Depois que o workflow terminar, baixe os artefatos e valide:

```bash
sha256sum --check SHA256SUMS-vX.Y.Z.txt
```

No PowerShell, compare cada valor com
`(Get-FileHash <arquivo> -Algorithm SHA256).Hash`.

## Origem das ferramentas

As configurações seguem os projetos oficiais:

- [GitHub Actions checkout](https://github.com/actions/checkout);
- [GitHub Actions setup-python](https://github.com/actions/setup-python);
- [GitHub Dependency Review](https://github.com/actions/dependency-review-action);
- [Gitleaks Action](https://github.com/gitleaks/gitleaks-action);
- [pip-audit](https://github.com/pypa/gh-action-pip-audit);
- [Anchore SBOM Action](https://github.com/anchore/sbom-action).

As versões das Actions são acompanhadas pelo Dependabot. Mudanças de versão
principal exigem revisão explícita.
