param(
    [switch]$Uninstall,
    [switch]$u
)

$TargetDir = "TF2-Key-calc"
$ZipUrl = "https://github.com/Rockeyxx/TF2-Key-calc/archive/refs/heads/main.zip"

if ($Uninstall -or $u) {
    Write-Host "[*] Uninstalling TF2 Key Calculator setup..." -ForegroundColor Yellow
    if (Test-Path ".venv") {
        Write-Host " -> Removing virtual environment (.venv)..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force ".venv"
    }
    if (Test-Path "prices_cache.json") {
        Write-Host " -> Removing cached prices (prices_cache.json)..." -ForegroundColor Yellow
        Remove-Item -Force "prices_cache.json"
    }
    if (Test-Path "storage") {
        Write-Host " -> Removing Crawlee storage directory..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "storage"
    }
    Write-Host "[+] Cleanup completed successfully." -ForegroundColor Green
    return
}

# --- Find Python ---
function Find-Python {
    foreach ($candidate in @("py", "python3", "python")) {
        try {
            $out = & $candidate --version 2>&1
            if ($out -match "Python \d") {
                return $candidate
            }
        } catch {}
    }
    return $null
}

$PY = Find-Python

if (-not $PY) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Python is not installed               " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Python, run this in PowerShell:" -ForegroundColor Yellow
    Write-Host '  winget install -e --id Python.Python.3.12' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or download manually:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host '  (CHECK "Add Python to PATH" during install)' -ForegroundColor Green
    Write-Host ""
    Write-Host "Then close and reopen PowerShell and run this script again." -ForegroundColor Yellow
    Write-Host ""
    return
}

Write-Host "[+] Using: $PY ($( & $PY --version 2>&1 ))" -ForegroundColor Green

# --- Download repo if needed ---
if (-not (Test-Path "Calc.py")) {
    if (-not (Test-Path $TargetDir)) {
        Write-Host "[*] Downloading TF2-Key-calc..." -ForegroundColor Cyan
        $ZipPath = Join-Path $env:TEMP "TF2-Key-calc-main.zip"
        Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -UseBasicParsing
        Expand-Archive -Path $ZipPath -DestinationPath "." -Force
        Remove-Item -Force $ZipPath
        if (Test-Path "TF2-Key-calc-main") {
            Rename-Item -Path "TF2-Key-calc-main" -NewName $TargetDir
        }
    }
    if (Test-Path $TargetDir) {
        Set-Location $TargetDir
    }
}

# --- Setup venv ---
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Setting up Python virtual environment..." -ForegroundColor Cyan
    & $PY -m venv .venv
}

try {
    & .\.venv\Scripts\Activate.ps1
} catch {
    $env:PATH = "$(Get-Location)\.venv\Scripts;" + $env:PATH
}

# --- Install deps & run ---
Write-Host "[*] Installing Python dependencies..." -ForegroundColor Cyan
& $PY -m pip install --quiet "crawlee[playwright]" httpx
& $PY -m playwright install chromium

Write-Host "[*] Starting TF2 Key Calculator..." -ForegroundColor Green
& $PY Calc.py
