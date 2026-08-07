# Crawlee TF2 Key Price Scraper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate Crawlee (`crawlee[playwright]`) into `Calc.py` to fetch live TF2 key prices from MannCo.store, DMarket, and Steam Market on startup, with automatic fallbacks.

**Architecture:** A modular scraper (`price_fetcher.py`) uses Crawlee to fetch live prices from MannCo.store, DMarket, and Steam Market. `Calc.py` calls `price_fetcher.py` on startup to automatically supply live market values to the key calculations.

**Tech Stack:** Python 3.14, `crawlee[playwright]`, `httpx`, `asyncio`, `unittest`.

## Global Constraints
- Always prefix shell commands with `rtk`.
- Fallbacks if network or scraping fails: MannCo: 1.73 USD, DMMarket: 1.63 USD, Steam: 99.0 UAH.
- Non-blocking error handling to ensure `Calc.py` never crashes if scraping fails.

---

### Task 1: Install Dependencies
**Files:**
- Create: None
- Modify: `requirements.txt` (or install directly)

- [ ] **Step 1: Install crawlee with playwright support**
Run: `rtk pip install "crawlee[playwright]" httpx`
Expected: `crawlee` and `httpx` successfully installed.

- [ ] **Step 2: Install Playwright Chromium browser**
Run: `rtk python3 -m playwright install chromium`
Expected: Chromium browser installed for Playwright.

---

### Task 2: Create Price Fetcher Module (`price_fetcher.py`)
**Files:**
- Create: `price_fetcher.py`
- Test: `test_price_fetcher.py`

**Interfaces:**
- Produces: `fetch_live_prices() -> dict` with keys `{'mannco_usd': float, 'dmarket_usd': float, 'steam_uah': float}`

- [ ] **Step 1: Write failing unit test for fallback values**
Create `test_price_fetcher.py`:
```python
import unittest
from price_fetcher import fetch_fallback_prices

class TestPriceFetcher(unittest.TestCase):
    def test_fallback_prices(self):
        prices = fetch_fallback_prices()
        self.assertEqual(prices['mannco_usd'], 1.73)
        self.assertEqual(prices['dmarket_usd'], 1.63)
        self.assertEqual(prices['steam_uah'], 99.0)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**
Run: `rtk python3 -m unittest test_price_fetcher.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'price_fetcher'`

- [ ] **Step 3: Implement `price_fetcher.py` with Crawlee & Steam API scraper**
Create `price_fetcher.py`:
```python
import asyncio
import re
import httpx
from crawlee.playwright import PlaywrightCrawler, PlaywrightCrawlingContext

DEFAULT_PRICES = {
    'mannco_usd': 1.73,
    'dmarket_usd': 1.63,
    'steam_uah': 99.0
}

def fetch_fallback_prices():
    return DEFAULT_PRICES.copy()

async def _fetch_steam_price_uah() -> float:
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "appid": 440,
        "market_hash_name": "Mann Co. Supply Crate Key",
        "currency": 18
    }
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(url, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                raw_price = data.get("lowest_price", "0")
                clean = raw_price.replace("₴", "").replace(",", ".").replace(" ", "").strip()
                match = re.search(r"(\d+(?:\.\d+)?)", clean)
                if match:
                    return float(match.group(1))
    return DEFAULT_PRICES['steam_uah']

async def _scrape_mannco_and_dmarket() -> dict:
    scraped = {}

    crawler = PlaywrightCrawler(
        max_requests_per_crawl=2,
        request_handler_timeout=15.0,
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        url = context.request.url
        page = context.page
        if "mannco.store" in url:
            # Wait for price element
            try:
                elem = await page.wait_for_selector(".price, [class*='price']", timeout=5000)
                if elem:
                    text = await elem.inner_text()
                    match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
                    if match:
                        scraped['mannco_usd'] = float(match.group(1))
            except Exception:
                pass
        elif "dmarket.com" in url:
            try:
                elem = await page.wait_for_selector("[class*='price']", timeout=5000)
                if elem:
                    text = await elem.inner_text()
                    match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
                    if match:
                        scraped['dmarket_usd'] = float(match.group(1))
            except Exception:
                pass

    await crawler.run([
        "https://mannco.store/item/440-mann-co-supply-crate-key",
        "https://dmarket.com/ingame-items/item-list/tf2-skins?title=mann%20co.%20supply%20crate%20key"
    ])
    return scraped

def fetch_live_prices() -> dict:
    prices = fetch_fallback_prices()
    try:
        steam_price = asyncio.run(_fetch_steam_price_uah())
        prices['steam_uah'] = steam_price
    except Exception as e:
        print(f"[!] Warning: Could not fetch Steam price ({e}). Using default {prices['steam_uah']} UAH.")

    try:
        crawlee_prices = asyncio.run(_scrape_mannco_and_dmarket())
        if 'mannco_usd' in crawlee_prices:
            prices['mannco_usd'] = crawlee_prices['mannco_usd']
        if 'dmarket_usd' in crawlee_prices:
            prices['dmarket_usd'] = crawlee_prices['dmarket_usd']
    except Exception as e:
        print(f"[!] Warning: Crawlee scraping error ({e}). Using fallbacks for Mannco/DMMarket.")

    return prices
```

- [ ] **Step 4: Run unit test to verify fallback test passes**
Run: `rtk python3 -m unittest test_price_fetcher.py`
Expected: PASS

---

### Task 3: Integrate `price_fetcher.py` into `Calc.py`
**Files:**
- Modify: `Calc.py`

- [ ] **Step 1: Update `Calc.py` to import and fetch live prices on launch**
In `Calc.py`, import `fetch_live_prices` and fetch initial default parameters dynamically when `Calc.py` runs.

- [ ] **Step 2: Verify `Calc.py` runs cleanly**
Run: `rtk python3 Calc.py` (simulated execution)
Expected: Prints live/fallback prices and prompts user.
