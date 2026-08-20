param(
    [switch]$Uninstall,
    [switch]$u,
    [switch]$Update,
    [switch]$Run,
    [switch]$r,
    [switch]$Help,
    [switch]$h
)

$TargetDir = "TF2-Key-calc"
$ZipUrl = "https://github.com/Rockeyxx/TF2-Key-calc/archive/refs/heads/main.zip"
$RepoUrl = "https://github.com/Rockeyxx/TF2-Key-calc.git"

function Do-Uninstall {
    Write-Host ""
    Write-Host "[*] Uninstalling TF2 Key Calculator setup..." -ForegroundColor Yellow
    if ((Test-Path $TargetDir) -and -not (Test-Path "Calc.py")) {
        Set-Location $TargetDir
    }
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
}

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

function Ensure-Repo {
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
    # If git is available and repo has .git, pull latest updates
    if (Test-Path ".git") {
        try {
            & git pull --quiet origin main 2>$null
        } catch {}
    }
}

function Ensure-Venv-And-Deps ($PY) {
    if (-not (Test-Path ".venv")) {
        Write-Host "[*] Setting up Python virtual environment..." -ForegroundColor Cyan
        & $PY -m venv .venv
    }

    try {
        & .\.venv\Scripts\Activate.ps1
    } catch {
        $env:PATH = "$(Get-Location)\.venv\Scripts;" + $env:PATH
    }

    Write-Host "[*] Checking & installing Python dependencies..." -ForegroundColor Cyan
    & $PY -m pip install --quiet "crawlee[playwright]" httpx
    & $PY -m playwright install chromium
}

function Run-Calculator {
    $PY = Find-Python
    if (-not $PY) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "  Python is not installed               " -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "To install Python, run in PowerShell:" -ForegroundColor Yellow
        Write-Host '  winget install -e --id Python.Python.3.12' -ForegroundColor Cyan
        return
    }

    Ensure-Repo
    Ensure-Venv-And-Deps $PY
    Write-Host "[*] Starting TF2 Key Calculator..." -ForegroundColor Green
    & $PY Calc.py
}

function Do-Update {
    $PY = Find-Python
    if (-not $PY) { return }
    Ensure-Repo
    if (Test-Path ".venv") {
        Write-Host "[*] Updating Python dependencies..." -ForegroundColor Cyan
        & $PY -m pip install --quiet --upgrade "crawlee[playwright]" httpx
        & $PY -m playwright install chromium
    }
    Write-Host "[+] Update completed successfully." -ForegroundColor Green
}

# --- CLI Flag Handling ---
if ($Uninstall -or $u) {
    Do-Uninstall
    return
}
if ($Update) {
    Do-Update
    return
}
if ($Run -or $r) {
    Run-Calculator
    return
}
if ($Help -or $h) {
    Write-Host "Usage: .\run.ps1 [OPTIONS]"
    Write-Host "Options:"
    Write-Host "  -Run, -r         Run calculator directly"
    Write-Host "  -Update          Update repository and dependencies"
    Write-Host "  -Uninstall, -u   Remove virtual environment and caches"
    Write-Host "  -Help, -h        Show this help message"
    return
}

# --- Interactive Choice Menu ---
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       TF2 Key Price Calculator           " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  (1) Run Calculator [Default]"
Write-Host "  (2) Update to Latest Version"
Write-Host "  (3) Uninstall / Clean up"
Write-Host "  (4) Exit"
Write-Host "==========================================" -ForegroundColor Cyan

$choice = Read-Host "Enter choice (1-4) [default: 1]"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

switch ($choice) {
    "1" { Run-Calculator }
    "2" { Do-Update }
    "3" { Do-Uninstall }
    "4" { Write-Host "Exiting."; return }
    "q" { Write-Host "Exiting."; return }
    default {
        Write-Host "[!] Unknown option '$choice'. Defaulting to running calculator..." -ForegroundColor Yellow
        Run-Calculator
    }
}
