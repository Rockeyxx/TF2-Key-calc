#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/Rockeyxx/TF2-Key-calc.git"
TARGET_DIR="TF2-Key-calc"

# Helper function to read input even when piped (e.g. curl ... | bash)
prompt_user() {
    local prompt_msg="$1"
    local default_val="$2"
    local user_val=""
    if [ -e /dev/tty ]; then
        read -r -p "$prompt_msg" user_val < /dev/tty
    else
        read -r -p "$prompt_msg" user_val || true
    fi
    if [ -z "$user_val" ]; then
        echo "$default_val"
    else
        echo "$user_val"
    fi
}

do_uninstall() {
    echo ""
    echo "[*] Uninstalling TF2 Key Calculator setup..."
    if [ -d "$TARGET_DIR" ] && [ ! -f "Calc.py" ]; then
        cd "$TARGET_DIR"
    fi

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
}

ensure_repo() {
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

    # If it's a git repository, pull latest changes to keep code up to date
    if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
        echo "[*] Checking for updates..."
        git pull --quiet origin main || true
    fi
}

do_update() {
    ensure_repo
    echo "[*] Updating dependencies and environment..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        pip install --quiet --upgrade "crawlee[playwright]" httpx
        python3 -m playwright install chromium > /dev/null 2>&1 || python3 -m playwright install chromium
    fi
    echo "[+] Update completed successfully."
}

ensure_venv_and_deps() {
    if [ ! -d ".venv" ]; then
        echo "[*] Setting up Python virtual environment..."
        python3 -m venv .venv
    fi

    source .venv/bin/activate

    echo "[*] Checking & installing Python dependencies..."
    pip install --quiet "crawlee[playwright]" httpx

    python3 -m playwright install chromium > /dev/null 2>&1 || python3 -m playwright install chromium
}

run_calculator() {
    ensure_repo
    ensure_venv_and_deps
    echo "[*] Starting TF2 Key Calculator..."
    if [ -e /dev/tty ]; then
        python3 Calc.py < /dev/tty
    else
        python3 Calc.py
    fi
}

# --- CLI Flag Handling ---
if [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
    do_uninstall
    exit 0
elif [ "$1" = "--update" ]; then
    do_update
    exit 0
elif [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    run_calculator
    exit 0
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./run.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  (no arguments)     Open interactive menu"
    echo "  --run, -r          Run calculator directly"
    echo "  --update           Update repository and dependencies"
    echo "  --uninstall, -u    Remove virtualenv, cached prices, and storage"
    echo "  --help, -h         Show this help message"
    exit 0
fi

# --- Interactive Menu (When run without flags or via curl | bash) ---
echo ""
echo "=========================================="
echo "       TF2 Key Price Calculator"
echo "=========================================="
echo "  (1) Run Calculator [Default]"
echo "  (2) Update to Latest Version"
echo "  (3) Uninstall / Clean up"
echo "  (4) Exit"
echo "=========================================="
menu_choice=$(prompt_user "Enter choice (1-4) [default: 1]: " "1")

case "$menu_choice" in
    1)
        run_calculator
        ;;
    2)
        do_update
        ;;
    3)
        do_uninstall
        ;;
    4|"q"|"Q"|"exit")
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "[!] Unknown option '$menu_choice'. Defaulting to running calculator..."
        run_calculator
        ;;
esac
