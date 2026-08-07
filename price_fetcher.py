from datetime import timedelta
import asyncio
import re
import httpx
try:
    from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
    CRAWLEE_AVAILABLE = True
except ImportError:
    CRAWLEE_AVAILABLE = False

DEFAULT_PRICES = {
    'mannco_usd': 1.73,
    'dmarket_usd': 1.63,
    'steam_uah': 99.0
}

def fetch_fallback_prices() -> dict:
    """Returns fallback static prices."""
    return DEFAULT_PRICES.copy()

async def _fetch_steam_price_uah() -> float:
    """Fetches the lowest market sell price for TF2 Key in Ukrainian Hryvnia from Steam."""
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "appid": 440,
        "market_hash_name": "Mann Co. Supply Crate Key",
        "currency": 18
    }
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=8.0) as client:
        res = await client.get(url, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                raw_price = data.get("lowest_price", "") or data.get("median_price", "")
                clean = raw_price.replace("₴", "").replace(",", ".").replace(" ", "").strip()
                match = re.search(r"(\d+(?:\.\d+)?)", clean)
                if match:
                    return float(match.group(1))
    return DEFAULT_PRICES['steam_uah']

async def _fetch_dmarket_api() -> float | None:
    """Tries fetching price directly from DMarket public items API."""
    url = "https://api.dmarket.com/marketplace-api/v1/market-items"
    params = {
        "gameId": "tf2",
        "title": "Mann Co. Supply Crate Key",
        "limit": 1,
        "currency": "USD"
    }
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url, params=params, headers=headers)
            if res.status_code == 200:
                data = res.json()
                objects = data.get("objects", [])
                if objects:
                    price_usd = objects[0].get("price", {}).get("USD", "")
                    if price_usd:
                        # Price is often in cents (e.g. "165")
                        val = float(price_usd)
                        if val > 50: # if in cents
                            val = val / 100.0
                        return round(val, 2)
    except Exception:
        pass
    return None

async def _scrape_crawlee() -> dict:
    """Uses Crawlee PlaywrightCrawler to extract live prices from MannCo and DMarket."""
    if not CRAWLEE_AVAILABLE:
        print("[!] Notice: Crawlee module not installed in current Python environment. Using fallback prices.")
        return {}

    scraped = {}

    crawler = PlaywrightCrawler(
        max_requests_per_crawl=2,
        request_handler_timeout=timedelta(seconds=15),
        headless=True,
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        url = context.request.url
        page = context.page

        if "mannco.store" in url:
            try:
                # Wait for price element on page
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
                elem = await page.wait_for_selector("asset-card-price, .c-assetCard__price, [class*='assetCard'] [class*='price'], .price-value", timeout=10000)
                if elem:
                    text = await elem.inner_text()
                    match = re.search(r"\$?(\d+\.\d{2})", text)
                    if match:
                        scraped['dmarket_usd'] = float(match.group(1))
            except Exception as err:
                print(f"[!] DMarket crawl notice: {err}")

    await crawler.run([
        "https://mannco.store/item/440-mann-co-supply-crate-key",
        "https://dmarket.com/ingame-items/item-list/tf2-skins?title=mann%20co.%20supply%20crate%20key"
    ])

    return scraped

def fetch_live_prices() -> dict:
    """Fetches live market prices with fallbacks on failure."""
    prices = fetch_fallback_prices()

    print("[*] Fetching live TF2 key prices (Steam, MannCo, DMarket)...")

    # 1. Fetch Steam Market UAH price
    try:
        steam_val = asyncio.run(_fetch_steam_price_uah())
        prices['steam_uah'] = steam_val
    except Exception as e:
        print(f"[!] Could not fetch Steam live price: {e}. Using fallback {prices['steam_uah']} UAH.")

    # 2. Try DMarket direct API first for fast lookup
    try:
        dm_api_val = asyncio.run(_fetch_dmarket_api())
        if dm_api_val:
            prices['dmarket_usd'] = dm_api_val
    except Exception:
        pass

    # 3. Crawlee Playwright scrape for MannCo / DMarket if missing
    try:
        crawlee_results = asyncio.run(_scrape_crawlee())
        if 'mannco_usd' in crawlee_results:
            prices['mannco_usd'] = crawlee_results['mannco_usd']
        if 'dmarket_usd' in crawlee_results:
            prices['dmarket_usd'] = crawlee_results['dmarket_usd']
    except Exception as e:
        print(f"[!] Crawlee scrape notice: {e}. Using fallback prices where needed.")

    return prices
