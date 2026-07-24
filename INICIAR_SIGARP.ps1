[CmdletBinding()]
param([switch]$SemBuild, [switch]$NaoAbrirNavegador)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path -LiteralPath ".env")) {
    throw "O arquivo .env nao existe. Consulte INSTALAR_V0.10.0_ALPHA1.md."
}

Write-Host "Iniciando o SIGARP..." -ForegroundColor Cyan
if ($SemBuild) {
    docker compose up -d postgres backend
}
else {
    docker compose up -d --build postgres backend
}
if ($LASTEXITCODE -ne 0) {
    throw "O Docker Compose nao conseguiu iniciar o SIGARP."
}

$healthUrl = "http://127.0.0.1:8000/api/v1/health"
$consultaUrl = "http://127.0.0.1:8000/consulta"
$online = $false
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 3
        if ($health.status -eq "online") {
            $online = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $online) {
    docker compose ps
    docker compose logs --tail 80 backend
    throw "A API nao ficou disponivel em ate 60 segundos."
}

Write-Host "SIGARP $($health.version) online." -ForegroundColor Green
Write-Host "Consulta: $consultaUrl"
if (-not $NaoAbrirNavegador) {
    Start-Process $consultaUrl
}
