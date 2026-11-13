# TF2 Key Price Calculator & Live Scraper

A Python utility and web scraper designed for Team Fortress 2 (TF2) key trading and Steam wallet conversions. It calculates total purchase costs across key marketplaces (**MannCo.store**, **DMarket** and **SIH Market**) in **USD** and **SAR (Saudi Riyal)**, and computes the exact **UAH (Ukrainian Hryvnia)** balance you receive in your Steam wallet after Steam market transaction fees.

---

## Features

- **Automated Live Web Scraping (`Crawlee` & `Playwright`)**:
- Automatically fetches real-time TF2 key prices from **MannCo.store**, **DMarket** and **SIH Market** (sorted by _Lowest Price_).
- Fetches live key market prices in Ukrainian Hryvnia directly from **Steam Community Market**.
- Includes robust offline fallbacks if a network error occurs.
- **Dual Calculation Modes**:
  - **By Game Price**: Input a game's price in UAH, and it computes how many keys you need to buy and the cost across stores.
  - **By Key Quantity**: Input the number of keys you want to buy to get a full cost breakdown.
- **Accurate Marketplace Fee Modeling**:
- **MannCo.store**: Includes the Google Pay / Apple Pay checkout fee (3.9% + $0.40, same as Card).
- **DMarket**: Includes the Google Pay / Apple Pay deposit fee (2.35% + $0.25, same as Card, added on top so the fee is covered).
- **SIH Market**: Includes the Card deposit fee (3% + $0.25, minimum $1 deposit); SIH has no Google Pay / Apple Pay option.
- **Steam Market**: Deducts Steam's 15% transaction fee ($1.15$ divisor) to output exact wallet gain in UAH.

---

## Download

Grab a launcher from the [latest release](https://github.com/Rockeyxx/TF2-Key-calc/releases/latest). Each one sets up Python dependencies and pulls the latest calculator from `main` every time it runs.

- **Windows:** download `run.bat` and double-click it (Python 3 must be installed).
- **Linux / macOS:** download `run.sh` and run `bash run.sh` in the folder you saved it to.

---

## Quick Start (One-Line Run)

Run the calculator directly in your terminal with a single command (automatically sets up or updates the environment & dependencies):

### Linux / macOS:

```bash
bash <(curl -sSL https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.sh)
```
or:
```bash
curl -sSL https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.sh | bash
```

### Windows (PowerShell):

```powershell
iwr -useb https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.ps1 | iex
```

> **Interactive Menu:** Running the command presents an interactive menu with choices:
> 1. `(1) Run Calculator [Default]`
> 2. `(2) Update to Latest Version`
> 3. `(3) Uninstall / Clean up`

### Uninstalling / Cleanup

You can either select option `(3)` in the interactive menu, or pass direct flags:

- **Linux / macOS:** `./run.sh --uninstall` (or `bash <(curl -sSL https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.sh) --uninstall`)
- **Windows (PowerShell):** `.\run.ps1 -Uninstall`

---

## Manual Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rockeyxx/TF2-Key-calc.git
cd TF2-Key-calc
```

### 2. Set up virtual environment & dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "crawlee[playwright]" httpx
python3 -m playwright install chromium
```

---

## Usage

Run the main calculator script:

```bash
python Calc.py
```

### Interactive Output Example:

```text
[*] Fetching live TF2 key prices (Steam, MannCo, DMarket, SIH)...

[+] Active Prices Loaded: MannCo $1.77 | DMMarket $1.75 | SIH $1.703 | Steam 100.0 UAH

Choose (0) for game price (1) for keys number: 0
Enter the game price: 330

Keys needed: 4
Mannco (Key price: $1.77, Google Pay/Apple Pay):
 Pay: 29.1 SAR ($7.76)
 Steam wallet after selling: 347.83 UAH
DMMarket (Key price: $1.75, Google Pay/Apple Pay):
 Pay: 27.82 SAR ($7.42)
 Steam wallet after selling: 347.83 UAH
SIH Market (Key price: $1.703, Card):
 Pay: 27.38 SAR ($7.3)
 Steam wallet after selling: 347.83 UAH
```
---

## Built With

- **[Python 3](https://www.python.org/)** - Core logic
- **[Crawlee Python](https://crawlee.dev/python)** - High-performance Playwright web scraping
- **[Playwright](https://playwright.dev/python)** - Dynamic JavaScript rendering
- **[httpx](https://www.python-httpx.org/)** - Async HTTP requests for Steam API
