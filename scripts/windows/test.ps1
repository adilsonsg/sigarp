$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "../..")
docker compose run --rm backend pytest -v
