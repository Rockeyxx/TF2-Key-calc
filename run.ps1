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
    exit 0
}

# --- Find or install Python ---
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
    Write-Host "[!] Python not found. Attempting to install via winget..." -ForegroundColor Yellow
    try {
        winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        # Refresh PATH so the new install is visible
        $env:PATH = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        $PY = Find-Python
    } catch {
        Write-Host "[!] winget not available." -ForegroundColor Red
    }
}

if (-not $PY) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Python could not be found or installed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python manually:" -ForegroundColor Yellow
    Write-Host "  1. Go to https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "  2. Download and run the installer" -ForegroundColor Cyan
    Write-Host '  3. CHECK "Add Python to PATH" during install' -ForegroundColor Green
    Write-Host "  4. Close and reopen PowerShell, then run this script again" -ForegroundColor Cyan
    Write-Host ""
    exit 1
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
