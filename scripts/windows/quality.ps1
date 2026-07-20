$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "../..")
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
