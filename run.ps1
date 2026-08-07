$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/Rockeyxx/TF2-Key-calc.git"
$TargetDir = "TF2-Key-calc"

if (-not (Test-Path "Calc.py")) {
    if (-not (Test-Path $TargetDir)) {
        Write-Host "[*] Cloning TF2-Key-calc repository..." -ForegroundColor Cyan
        git clone $RepoUrl $TargetDir
    }
    Set-Location $TargetDir
}

if (-not (Test-Path ".venv")) {
    Write-Host "[*] Setting up Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

try {
    & .\.venv\Scripts\Activate.ps1
} catch {
    # If PowerShell script execution policy restricts activation script
    $env:PATH = "$(Get-Location)\.venv\Scripts;" + $env:PATH
}

Write-Host "[*] Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --quiet "crawlee[playwright]" httpx
python -m playwright install chromium

Write-Host "[*] Starting TF2 Key Calculator..." -ForegroundColor Green
python Calc.py
