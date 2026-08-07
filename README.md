# TF2 Key Price Calculator & Live Scraper

A Python utility and web scraper designed for Team Fortress 2 (TF2) key trading and Steam wallet conversions. It calculates total purchase costs across key marketplaces (**MannCo.store** and **DMarket**) in **USD** and **SAR (Saudi Riyal)**, and computes the exact **UAH (Ukrainian Hryvnia)** balance you receive in your Steam wallet after Steam market transaction fees.

---

## Features

- **Automated Live Web Scraping (`Crawlee` & `Playwright`)**:
- Automatically fetches real-time TF2 key prices from **MannCo.store** and **DMarket** (sorted by _Lowest Price_).
- Fetches live key market prices in Ukrainian Hryvnia directly from **Steam Community Market**.
- Includes robust offline fallbacks if a network error occurs.
- **Dual Calculation Modes**:
  - **By Game Price**: Input a game's price in UAH, and it computes how many keys you need to buy and the cost across stores.
  - **By Key Quantity**: Input the number of keys you want to buy to get a full cost breakdown.
- **Accurate Marketplace Fee Modeling**:
- **MannCo.store**: Includes baseline percentage and flat transaction fees.
- **DMarket**: Includes percentage fee model.
- **Steam Market**: Deducts Steam's 15% transaction fee ($1.15$ divisor) to output exact wallet gain in UAH.

---

## Quick Start (One-Line Run)

Run the calculator directly in your terminal with a single command (automatically sets up virtual environment & dependencies):

### Linux / macOS:

```bash
curl -sSL https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.sh | bash
```

### Windows (PowerShell):

```powershell
iwr -useb https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.ps1 | iex
```

### Uninstalling / Cleanup

To clean up the virtual environment, cached prices, and storage:

- **Linux / macOS:** `./run.sh --uninstall`
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
[*] Fetching live TF2 key prices (Steam, MannCo, DMarket)...

[+] Active Prices Loaded: MannCo $1.77 | DMMarket $1.75 | Steam 100.0 UAH

Choose (0) for game price (1) for keys number: 0
Enter the game price: 330

Keys needed: 4
Mannco (Key price: $1.77): 28.5 SAR | 7.6 USD |
 you will get in steam account 347.83 UAH

DMMarket (Key price: $1.75): 25.95 SAR | 6.92 USD |
 you will get in steam account 347.83 UAH
```

---

## Testing

Run the included unit test suite covering key math calculations and price fetcher fallbacks:

```bash
python -m unittest test_calc.py test_price_fetcher.py
```

---

## Built With

- **[Python 3](https://www.python.org/)** - Core logic
- **[Crawlee Python](https://crawlee.dev/python)** - High-performance Playwright web scraping
- **[Playwright](https://playwright.dev/python)** - Dynamic JavaScript rendering
- **[httpx](https://www.python-httpx.org/)** - Async HTTP requests for Steam API
