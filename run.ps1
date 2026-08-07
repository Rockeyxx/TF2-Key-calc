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

# Detect the correct Python command (py > python3 > python)
$PythonCmd = $null
foreach ($cmd in @("py", "python3", "python")) {
    try {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            # Verify it's real Python, not the Windows Store alias
            $ver = & $cmd --version 2>&1
            if ($ver -match "Python \d") {
                $PythonCmd = $cmd
                break
            }
        }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Host "[!] Python is not installed. Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "    Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Using Python command: $PythonCmd" -ForegroundColor Green

if (-not (Test-Path ".venv")) {
    Write-Host "[*] Setting up Python virtual environment..." -ForegroundColor Cyan
    & $PythonCmd -m venv .venv
}

try {
    & .\.venv\Scripts\Activate.ps1
} catch {
    $env:PATH = "$(Get-Location)\.venv\Scripts;" + $env:PATH
}

Write-Host "[*] Installing Python dependencies..." -ForegroundColor Cyan
& $PythonCmd -m pip install --quiet "crawlee[playwright]" httpx
& $PythonCmd -m playwright install chromium

Write-Host "[*] Starting TF2 Key Calculator..." -ForegroundColor Green
& $PythonCmd Calc.py

