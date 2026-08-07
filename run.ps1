param(
    [switch]$Uninstall,
    [switch]$u
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/Rockeyxx/TF2-Key-calc.git"
$TargetDir = "TF2-Key-calc"

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

if (-not (Test-Path "Calc.py")) {
    if (-not (Test-Path $TargetDir)) {
        $hasGit = $false
        try {
            $cmd = Get-Command "git" -ErrorAction SilentlyContinue
            if ($cmd) { $hasGit = $true }
        } catch {
            $hasGit = $false
        }

        if ($hasGit) {
            Write-Host "[*] Cloning TF2-Key-calc repository using git..." -ForegroundColor Cyan
            git clone $RepoUrl $TargetDir
        } else {
            Write-Host "[*] Git not found. Downloading repository ZIP archive..." -ForegroundColor Cyan
            $ZipPath = "$env:TEMP\TF2-Key-calc-main.zip"
            Invoke-WebRequest -Uri "https://github.com/Rockeyxx/TF2-Key-calc/archive/refs/heads/main.zip" -OutFile $ZipPath
            Expand-Archive -Path $ZipPath -DestinationPath "." -Force
            Remove-Item -Force $ZipPath
            if (Test-Path "TF2-Key-calc-main") {
                Rename-Item -Path "TF2-Key-calc-main" -NewName $TargetDir
            }
        }
    }
    if (Test-Path $TargetDir) {
        Set-Location $TargetDir
    }
}

if (-not (Test-Path ".venv")) {
    Write-Host "[*] Setting up Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

try {
    & .\.venv\Scripts\Activate.ps1
} catch {
    $env:PATH = "$(Get-Location)\.venv\Scripts;" + $env:PATH
}

Write-Host "[*] Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --quiet "crawlee[playwright]" httpx
python -m playwright install chromium

Write-Host "[*] Starting TF2 Key Calculator..." -ForegroundColor Green
python Calc.py
