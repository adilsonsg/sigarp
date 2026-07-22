# Instalação — SIGARP v0.7.0-alpha1

## Atualização desde v0.6.0-alpha1

Faça backup do PostgreSQL e preserve o `.env`. Gere tokens diferentes para cada
identidade. Exemplo PowerShell para um token de 256 bits:

```powershell
$bytes = New-Object byte[] 32
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
$token = [Convert]::ToBase64String($bytes)
$sha256 = [Security.Cryptography.SHA256]::Create()
$hash = [Convert]::ToHexString($sha256.ComputeHash(
  [Text.Encoding]::UTF8.GetBytes($token)
)).ToLowerInvariant()
$sha256.Dispose()
```

Guarde `$token` no cofre institucional. Adicione somente `$hash` ao JSON de uma
linha em `.env`:

```dotenv
AUTH_PRINCIPALS=[{"subject":"analista@ifmt.edu.br","name":"Pessoa Analista","role":"analista","token_sha256":"<hash>"}]
```

Esta versão remove a senha de banco herdada do repositório. Para um volume já
existente, troque-a antes de reiniciar o backend:

```powershell
docker exec -it sigarp_postgres psql -U sigarp -d sigarp
```

No prompt do `psql`, execute `\password sigarp`, informe uma senha hexadecimal
forte e saia com `\q`. Registre a mesma senha apenas no `.env` local:

```dotenv
POSTGRES_DB=sigarp
POSTGRES_USER=sigarp
POSTGRES_PASSWORD=<segredo-forte>
```

Faça essa rotação antes de qualquer novo comando `docker compose`. O Compose
recusa inicialização quando `POSTGRES_PASSWORD` está ausente ou vazio.
Senhas com caracteres reservados de URL devem ser codificadas; prefira 64
caracteres hexadecimais aleatórios.

Atualize e valide:

```bash
docker compose build backend
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend alembic current
docker compose run --rm backend pytest -q
docker compose up -d
```

O head esperado é `20260722_0010`. Sem `AUTH_PRINCIPALS` válido, rotas de dados
respondem `401`; health check e metadados OpenAPI permanecem públicos.

Valide a identidade sem imprimir o token em logs:

```powershell
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod http://127.0.0.1:8000/auth/me -Headers $headers
```

Não use `docker compose down -v`. Consulte `docs/security.md` para rotação e
implantação HTTPS.
