$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "../..")
docker compose up -d --build
docker compose exec backend alembic upgrade head
Write-Host "SIGARP iniciado em http://127.0.0.1:8000/docs"
