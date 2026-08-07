# Design Document: Crawlee Live Price Integration for TF2 Keys

**Date:** 2026-08-07  
**Topic:** Live TF2 Key Price Scraping using Crawlee

## Overview

Integrate Crawlee (`crawlee[playwright]`) into the TF2 Key calculator (`Calc.py`) to automatically fetch live key prices from MannCo.store, DMarket, and Steam Market on startup, with automatic fallbacks to static values if fetching fails.

## Targeted URLs & Extracted Data

1. **MannCo.store**: `https://mannco.store/item/440-mann-co-supply-crate-key` -> Lowest price in USD.
2. **DMarket**: `https://dmarket.com/ingame-items/item-list/tf2-skins?title=mann%20co.%20supply%20crate%20key` -> Lowest price in USD.
3. **Steam Market**: `https://steamcommunity.com/market/priceoverview/?appid=440&market_hash_name=Mann%20Co.%20Supply%20Crate%20Key&currency=18` -> Lowest sell price in UAH.

## Component Architecture

- `price_fetcher.py`:
  - Contains `fetch_live_prices()` function using Crawlee's `PlaywrightCrawler` and `httpx` / HTTP requests.
  - Implements robust error handling and timeout fallbacks (MannCo: `1.73` USD, DMMarket: `1.63` USD, Steam: `99.0` UAH).
  - Returns a clean dictionary with `mannco_usd`, `dmarket_usd`, and `steam_uah`.
- `Calc.py`:
  - Calls `fetch_live_prices()` on launch.
  - Overrides default parameters with scraped values dynamically.
- `test_price_fetcher.py`:
  - Unit tests verifying fallback mechanism and price extraction/sanitization.

## Error Handling & Fallbacks

- Timeout set to 10 seconds per target.
- If scraping fails for any reason (e.g. network offline, site layout changed, rate limited), the program logs a notice and uses default fallback prices without crashing.
