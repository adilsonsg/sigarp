# Validação — SIGARP v0.9.0-alpha1

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
- 78 testes aprovados;
- Ruff, Black e isort sem falhas;
- nenhuma alteração de schema PostgreSQL.

## Contrato da API v1

```powershell
$baseUrl = "http://127.0.0.1:8000"
$headers = @{ Authorization = "Bearer SEU_TOKEN_DE_LEITOR" }

$health = Invoke-RestMethod "$baseUrl/api/v1/health"
$page = Invoke-RestMethod `
    "$baseUrl/api/v1/orgaos?page=1&page_size=20" `
    -Headers $headers

$health | Select-Object application, version, environment, status
$page | Select-Object page, page_size, total, total_pages
$page.items | Select-Object -First 3
```

Para validar o erro e a correlação:

```powershell
try {
    Invoke-WebRequest `
        "$baseUrl/api/v1/orgaos?page=0" `
        -Headers $headers `
        -ErrorAction Stop
}
catch {
    $requestId = $_.Exception.Response.Headers["X-Request-ID"]
    $body = $_.ErrorDetails.Message | ConvertFrom-Json
    [pscustomobject]@{
        status = [int]$_.Exception.Response.StatusCode
        code = $body.code
        request_id_header = $requestId
        request_id_body = $body.request_id
    }
}
```

O status deve ser `422`, o código `validation_error` e os dois identificadores
devem ser iguais.

## OpenAPI e compatibilidade

Confirme em `http://127.0.0.1:8000/docs`:

- rotas canônicas sob `/api/v1`;
- respostas paginadas documentadas;
- `ErrorResponse` documentado nas respostas de erro;
- rotas legadas de dados marcadas como depreciadas.

## Critérios de aceite

- `/api/v1` é o contrato canônico;
- listas locais informam total sem truncamento silencioso;
- erros incluem `request_id`;
- testes automatizados verificam o OpenAPI;
- política de depreciação está publicada;
- rotas legadas continuam compatíveis durante a transição.
