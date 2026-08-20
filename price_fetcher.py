from datetime import timedelta
import asyncio
import re
import httpx
try:
    from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
    CRAWLEE_AVAILABLE = True
except ImportError:
    CRAWLEE_AVAILABLE = False

import json
import os
from datetime import datetime

CACHE_FILE_PATH = os.path.join(os.path.dirname(__file__), "prices_cache.json")

DEFAULT_PRICES = {
    'mannco_usd': 1.73,
    'dmarket_usd': 1.63,
    'steam_uah': 99.0
}

def fetch_fallback_prices() -> dict:
    """Returns fallback static prices."""
    return DEFAULT_PRICES.copy()

def load_cached_prices(cache_path: str = CACHE_FILE_PATH) -> dict | None:
    """Loads cached prices from JSON file if available."""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_cached_prices(prices: dict, currency_code: str = "UAH", currency_id: int = 18, cache_path: str = CACHE_FILE_PATH) -> None:
    """Saves fetched prices to JSON cache file."""
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "currency_code": currency_code,
        "currency_id": currency_id,
        "prices": prices
    }
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[!] Notice: Could not save cache: {e}")

async def _fetch_steam_price(currency_id: int = 18) -> float:
    """Fetches the sell key price for TF2 Key in chosen currency from Steam Market."""
    url = "https://steamcommunity.com/market/itemordershistogram"
    params = {
        "country": "US",
        "language": "english",
        "currency": currency_id,
        "item_nameid": 1
    }
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=8.0) as client:
        res = await client.get(url, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json()
            table_html = data.get("buy_order_table", "")
            rows = re.findall(r'<td[^>]*>([^<]+)</td>', table_html)
            prices = [r.strip() for idx, r in enumerate(rows) if idx % 2 == 0]
            if prices:
                raw_str = prices[-1]
                clean = re.search(r'(\d+(?:[.,]\d+)?)', raw_str.replace(',', '.'))
                if clean:
                    return float(clean.group(1))

    # Fallback to priceoverview
    url_fallback = "https://steamcommunity.com/market/priceoverview/"
    params_fallback = {"appid": 440, "market_hash_name": "Mann Co. Supply Crate Key", "currency": currency_id}
    async with httpx.AsyncClient(timeout=8.0) as client:
        res = await client.get(url_fallback, params=params_fallback, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                raw_price = data.get("lowest_price", "") or data.get("median_price", "")
                clean = raw_price.replace("₴", "").replace(",", ".").replace(" ", "").strip()
                match = re.search(r"(\d+(?:[.,]\d+)?)", clean)
                if match:
                    return float(match.group(1))
    return DEFAULT_PRICES['steam_uah']

async def _fetch_dmarket_api() -> float | None:
    """Fetches the 5 lowest key prices from DMarket API and takes the highest among them to eliminate outliers."""
    url = "https://api.dmarket.com/exchange/v1/market/items/v2"
    params = {
        "title": "mann co. supply crate key",
        "orderBy": "price",
        "orderDir": "asc",
        "isLoggedIn": "false",
        "gameId": "tf2",
        "pageSize": "20",
        "side": "market",
        "currency": "USD",
        "platform": "browser"
    }
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url, params=params, headers=headers)
            if res.status_code == 200:
                data = res.json()
                offers = data.get("offers", [])
                prices = []
                for offer in offers:
                    if "priceCents" in offer:
                        prices.append(round(offer["priceCents"] / 100.0, 2))
                    elif "price" in offer and "USD" in offer["price"]:
                        v = float(offer["price"]["USD"])
                        if v > 50:
                            v /= 100.0
                        prices.append(round(v, 2))
                if prices:
                    sorted_prices = sorted(prices)
                    least_5 = sorted_prices[:5]
                    selected_price = max(least_5)
                    return selected_price
    except Exception as e:
        print(f"[!] DMarket API fetch notice: {e}")
    return None

async def _scrape_crawlee(currency_id: int = 18) -> dict:
    """Uses Crawlee PlaywrightCrawler to extract live prices from MannCo, DMarket, and Steam."""
    if not CRAWLEE_AVAILABLE:
        print("[!] Notice: Crawlee module not installed in current Python environment. Using fallback prices.")
        return {}

    scraped = {}

    crawler = PlaywrightCrawler(
        max_requests_per_crawl=3,
        request_handler_timeout=timedelta(seconds=15),
        headless=True,
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        url = context.request.url
        page = context.page

        if "mannco.store" in url:
            try:
                elem = await page.wait_for_selector(".price, [class*='price']", timeout=6000)
                if elem:
                    text = await elem.inner_text()
                    match = re.search(r"\$?(\d+\.\d{2})", text)
                    if match:
                        scraped['mannco_usd'] = float(match.group(1))
            except Exception as err:
                print(f"[!] MannCo store crawl notice: {err}")

        elif "dmarket.com" in url:
            try:
                await page.set_viewport_size({'width': 1920, 'height': 1080})
                await page.wait_for_timeout(3000)
                
                # Open sort dropdown and select 'Price: Lowest First'
                await page.evaluate('''() => {
                    const btn = document.querySelector('.mat-mdc-menu-trigger, .o-select__sort');
                    if (btn) btn.click();
                }''')
                await page.wait_for_timeout(1000)
                
                await page.evaluate('''() => {
                    const fields = Array.from(document.querySelectorAll('.mdc-form-field, mat-radio-button, mat-option, label, div'));
                    for (const f of fields) {
                        if (f.innerText && f.innerText.trim() === 'Price: Lowest First') {
                            const target = f.querySelector('input, label') || f;
                            target.click();
                            return true;
                        }
                    }
                    return false;
                }''')
                await page.wait_for_timeout(3000)

                elements = await page.query_selector_all("asset-card-price, .c-assetCard__price, [class*='assetCard'] [class*='price'], .price-value")
                scraped_dmarket_prices = []
                for elem in elements:
                    text = await elem.inner_text()
                    match = re.search(r"\$?(\d+\.\d{2})", text)
                    if match:
                        scraped_dmarket_prices.append(float(match.group(1)))
                if scraped_dmarket_prices:
                    least_5 = sorted(scraped_dmarket_prices)[:5]
                    scraped['dmarket_usd'] = max(least_5)
            except Exception as err:
                print(f"[!] DMarket crawl notice: {err}")

        elif "steamcommunity.com" in url or "itemordershistogram" in url:
            try:
                body_content = await page.content()
                rows = re.findall(r'<td[^>]*>([^<]+)</td>', body_content)
                prices = [r.strip() for idx, r in enumerate(rows) if idx % 2 == 0]
                if prices:
                    raw_str = prices[-1]
                    clean = re.search(r'(\d+(?:[.,]\d+)?)', raw_str.replace(',', '.'))
                    if clean:
                        scraped['steam_uah'] = float(clean.group(1))
            except Exception as err:
                print(f"[!] Steam crawl notice: {err}")

    await crawler.run([
        "https://mannco.store/item/440-mann-co-supply-crate-key",
        "https://dmarket.com/ingame-items/item-list/tf2-skins?title=mann%20co.%20supply%20crate%20key",
        f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency={currency_id}&item_nameid=1"
    ])

    return scraped

def fetch_live_prices(currency_id: int = 18) -> dict:
    """Fetches live market prices with fallbacks on failure."""
    prices = fetch_fallback_prices()

    print("[*] Fetching live TF2 key prices (Steam, MannCo, DMarket)...")

    # 1. Fetch Steam Market price via httpx API
    try:
        steam_val = asyncio.run(_fetch_steam_price(currency_id=currency_id))
        prices['steam_uah'] = steam_val
    except Exception as e:
        print(f"[!] Could not fetch Steam live price: {e}. Using fallback {prices['steam_uah']}.")

    # 2. Fetch DMarket price via API (takes highest of 5 lowest to avoid outliers)
    try:
        dmarket_val = asyncio.run(_fetch_dmarket_api())
        if dmarket_val is not None:
            prices['dmarket_usd'] = dmarket_val
    except Exception as e:
        print(f"[!] Could not fetch DMarket API live price: {e}.")

    # 3. Crawlee Playwright scrape for MannCo, DMarket (if needed), and Steam
    try:
        crawlee_results = asyncio.run(_scrape_crawlee(currency_id=currency_id))
        if 'mannco_usd' in crawlee_results:
            prices['mannco_usd'] = crawlee_results['mannco_usd']
        if 'dmarket_usd' in crawlee_results and prices['dmarket_usd'] == DEFAULT_PRICES['dmarket_usd']:
            prices['dmarket_usd'] = crawlee_results['dmarket_usd']
        if 'steam_uah' in crawlee_results and prices['steam_uah'] == DEFAULT_PRICES['steam_uah']:
            prices['steam_uah'] = crawlee_results['steam_uah']
    except Exception as e:
        print(f"[!] Crawlee scrape notice: {e}. Using fallback prices where needed.")

    return prices
