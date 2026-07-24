[CmdletBinding()]
param(
    [datetime]$VigenteEm = (Get-Date).Date,
    [ValidateRange(1, 10000)][int]$LimitePaginas = 2,
    [ValidateSet("federal", "estadual", "municipal", "distrital")]
    [string]$Esfera = "federal"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

docker compose up -d postgres
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel iniciar o PostgreSQL."
}

$date = $VigenteEm.ToString("yyyy-MM-dd")
Write-Host "Consultando atas $Esfera vigentes em $date..." -ForegroundColor Cyan

docker compose run --rm backend `
    python -m app.cli.sync_pncp_price_registries `
    --inicio $date `
    --fim $date `
    --esfera $Esfera `
    --limite-paginas $LimitePaginas `
    --intervalo-paginas 1

if ($LASTEXITCODE -ne 0) {
    throw "A atualizacao das atas falhou."
}

Write-Host "Atas atualizadas. Abra http://127.0.0.1:8000/consulta" -ForegroundColor Green
