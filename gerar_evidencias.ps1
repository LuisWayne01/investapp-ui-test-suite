# Gera as evidências de execução do item 10.3 do roteiro.
# Uso (na pasta do projeto):
#   powershell -ExecutionPolicy Bypass -File gerar_evidencias.ps1
# Para rodar só um arquivo:
#   powershell -ExecutionPolicy Bypass -File gerar_evidencias.ps1 -Alvo tests/ui/test_auth_ui.py

param([string]$Alvo = "tests/ui")

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$py = ".\.venv\Scripts\python.exe"
$dir = "evidencias"
New-Item -ItemType Directory -Force $dir | Out-Null
if (Test-Path "reports\screenshots") { Remove-Item -Recurse -Force "reports\screenshots" }

Write-Host "`n=== 1/2 Execução headless: log completo do terminal (10.3 item 3) ===`n" -ForegroundColor Cyan
$inicio = Get-Date
$saida = & $py -m pytest $Alvo -v -s --html="$dir\relatorio.html" --self-contained-html 2>&1 | ForEach-Object { "$_" }
$saida | ForEach-Object { Write-Host $_ }
$cabecalho = "Comando: python -m pytest $Alvo -v -s`nData: $($inicio.ToString('dd/MM/yyyy HH:mm:ss'))`n"
($cabecalho + ($saida -join "`n")) | Out-File "$dir\log_terminal.txt" -Encoding utf8

Write-Host "`n=== 2/2 Execução headed (navegador visível, 10.3 item 2) ===" -ForegroundColor Cyan
Write-Host "Aperte Win+Shift+S quando a janela do Chromium estiver mostrando a aplicação.`n" -ForegroundColor Yellow
& $py -m pytest $Alvo --headed --slowmo 800 -q 2>&1 | ForEach-Object { Write-Host "$_" }

if (Test-Path "reports\screenshots") {
    Copy-Item -Recurse -Force "reports\screenshots" "$dir\screenshots"
}

Write-Host "`nEvidências geradas em: $((Resolve-Path $dir).Path)" -ForegroundColor Green
Write-Host "  - log_terminal.txt  (saída completa do pytest -v -s)"
Write-Host "  - relatorio.html    (relatório HTML com prints de cada teste)"
Write-Host "  - screenshots\      (print da tela final de cada teste)"
