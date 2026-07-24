[CmdletBinding()]
param(
    [datetime]$Inicio = (Get-Date).Date.AddDays(-30),
    [datetime]$Fim = (Get-Date).Date,
    [ValidateRange(1, 99)][int]$Modalidade = 6,
    [ValidatePattern("^[A-Za-z]{2}$")][string]$Uf,
    [ValidateRange(1, 10000)][int]$LimitePaginas,
    [switch]$IncluirSemSrp
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if ($Fim.Date -lt $Inicio.Date) {
    throw "A data final deve ser igual ou posterior a data inicial."
}

docker compose up -d postgres
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel iniciar o PostgreSQL."
}

function Invoke-SigarpCli {
    param([Parameter(Mandatory)][string[]]$Arguments)
    Write-Host "`n> python -m $($Arguments -join ' ')" -ForegroundColor Cyan
    docker compose run --rm backend python -m @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "A etapa '$($Arguments[0])' falhou."
    }
}

$syncArguments = @(
    "app.cli.sync_pncp",
    "--inicio", $Inicio.ToString("yyyy-MM-dd"),
    "--fim", $Fim.ToString("yyyy-MM-dd"),
    "--modalidade", $Modalidade.ToString(),
    "--intervalo-paginas", "1"
)
if ($Uf) {
    $syncArguments += @("--uf", $Uf.ToUpperInvariant())
}
if ($PSBoundParameters.ContainsKey("LimitePaginas")) {
    $syncArguments += @("--limite-paginas", $LimitePaginas.ToString())
}
if ($IncluirSemSrp) {
    $syncArguments += "--todas"
}

Write-Host "Atualizando contratacoes de $($Inicio.ToString('dd/MM/yyyy')) a $($Fim.ToString('dd/MM/yyyy'))..." -ForegroundColor Green
Invoke-SigarpCli $syncArguments
Invoke-SigarpCli @("app.cli.sync_pncp_items", "--somente-sem-itens", "--intervalo-requisicoes", "1")
Invoke-SigarpCli @("app.cli.classify_pncp_opportunities")
Invoke-SigarpCli @("app.cli.sync_pncp_documents", "--somente-candidatas", "--intervalo-requisicoes", "1")
Invoke-SigarpCli @("app.cli.analyze_pncp_documents", "--somente-candidatas", "--somente-pendentes", "--intervalo-requisicoes", "1")
Invoke-SigarpCli @("app.cli.classify_pncp_opportunities")

Write-Host "`nAtualizacao concluida." -ForegroundColor Green
Write-Host "Abra http://127.0.0.1:8000/consulta"
