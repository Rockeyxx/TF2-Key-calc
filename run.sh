#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/Rockeyxx/TF2-Key-calc.git"
TARGET_DIR="TF2-Key-calc"

# Check for uninstall flag
if [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
    echo "[*] Uninstalling TF2 Key Calculator setup..."
    if [ -d ".venv" ]; then
        echo " -> Removing virtual environment (.venv)..."
        rm -rf .venv
    fi
    if [ -f "prices_cache.json" ]; then
        echo " -> Removing cached prices (prices_cache.json)..."
        rm -f prices_cache.json
    fi
    if [ -d "storage" ]; then
        echo " -> Removing Crawlee storage directory..."
        rm -rf storage
    fi
    echo "[+] Cleanup completed successfully."
    exit 0
fi

# 1. If not already inside the project folder, clone or enter it
if [ ! -f "Calc.py" ]; then
    if [ ! -d "$TARGET_DIR" ]; then
        if command -v git >/dev/null 2>&1; then
            echo "[*] Cloning TF2-Key-calc repository..."
            git clone "$REPO_URL" "$TARGET_DIR"
        else
            echo "[*] Git not found. Downloading repository ZIP archive..."
            curl -sSL "https://github.com/Rockeyxx/TF2-Key-calc/archive/refs/heads/main.zip" -o main.zip
            unzip -q main.zip
            rm -f main.zip
            mv TF2-Key-calc-main "$TARGET_DIR"
        fi
    fi
    cd "$TARGET_DIR"
fi

# 2. Ensure virtualenv exists & activate
if [ ! -d ".venv" ]; then
    echo "[*] Setting up Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 3. Install required packages quietly
echo "[*] Checking & installing Python dependencies..."
pip install --quiet "crawlee[playwright]" httpx

# 4. Install Playwright browser if needed
python3 -m playwright install chromium > /dev/null 2>&1 || python3 -m playwright install chromium

# 5. Run calculator
echo "[*] Starting TF2 Key Calculator..."
if [ ! -t 0 ] && [ -c /dev/tty ]; then
    exec < /dev/tty 2>/dev/null || true
fi
python3 Calc.py

