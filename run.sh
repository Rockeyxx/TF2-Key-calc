#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/Rockeyxx/TF2-Key-calc.git"
TARGET_DIR="TF2-Key-calc"

# 1. If not already inside the project folder, clone or enter it
if [ ! -f "Calc.py" ]; then
    if [ ! -d "$TARGET_DIR" ]; then
        echo "[*] Cloning TF2-Key-calc repository..."
        git clone "$REPO_URL" "$TARGET_DIR"
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
python3 Calc.py
