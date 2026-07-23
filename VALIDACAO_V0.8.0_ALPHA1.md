# Validação — SIGARP v0.8.0-alpha1

## Código e banco

```powershell
docker compose run --rm backend alembic current
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
```

Resultados esperados:

- Alembic em `20260722_0010 (head)`;
- 72 testes aprovados;
- Ruff, Black e isort sem falhas;
- `pip-audit` sem vulnerabilidades conhecidas nas dependências fixadas.

## Aplicação

```powershell
$health = Invoke-RestMethod "http://127.0.0.1:8000/health"
$health | Select-Object application, version, environment, status
```

Resultado esperado: `SIGARP`, `0.8.0-alpha1`, ambiente configurado e `online`.
Repita a matriz de acesso e revisão da `0.7.0-alpha1`; esta versão não altera
autenticação, autorização nem o schema PostgreSQL.

## Segurança no GitHub

Em **Actions**, confirme:

- `Backend CI` aprovado;
- `Security / Varredura de segredos` aprovado;
- `Security / Auditoria de dependências Python` aprovado;
- `Security / Revisão de novas dependências` aprovado em pull requests.

Um achado real deve bloquear a integração. Não crie exclusão ampla para obter
resultado verde.

## Artefatos

Depois de publicar a release, confirme a presença do ZIP, da SBOM e do arquivo de
checksums. No PowerShell:

```powershell
$sums = Get-Content ".\SHA256SUMS-v0.8.0-alpha1.txt"
$sums
Get-FileHash ".\SIGARP-0.8.0-alpha1-release.zip" -Algorithm SHA256
Get-FileHash ".\SIGARP-v0.8.0-alpha1-sbom.spdx.json" -Algorithm SHA256
```

Os hashes calculados devem ser iguais aos registrados em `SHA256SUMS`.

## Critérios de aceite

- nenhuma credencial ou dado local está no Git;
- controles de CI e release passam;
- SBOM e checksums acompanham a tag;
- documentação aponta licença e decisões LGPD como pendências institucionais;
- a versão continua marcada como pré-release e não homologada para produção.
