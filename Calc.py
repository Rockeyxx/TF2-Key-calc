#Calculation the vlaue of tf2 key price from website and then the sell price in steam and the actual value you got to your account so you convert from ukraine to ryal saudi
import math

USD_TO_UAH = 41.5
USD_TO_SAR = 3.75

# Steam section
TF2KEY_PRICE = 99 #get_steam_price_uah() #UKRAININ 
STEAM_FEE = 1.15

def calculate_mannco_price(number_of_keys=1, tf2key_price=TF2KEY_PRICE, steam_fee=STEAM_FEE, usd_to_sar=USD_TO_SAR, key_price_usd=1.73):
    """Calculates total price for MannCo keys and returns a tuple (total_sar, total_usd, total_uah)."""
    fee_usd = round(0.06275 * number_of_keys + 0.305, 2)
    total_usd = round(fee_usd + key_price_usd * number_of_keys, 2)
    total_sar = round(total_usd * usd_to_sar, 2)
    total_uah = round((tf2key_price * number_of_keys) / steam_fee, 2)
    return (total_sar, total_usd, total_uah)

def calculate_dmmarket_price(number_of_keys=1, tf2key_price=TF2KEY_PRICE, steam_fee=STEAM_FEE, usd_to_sar=USD_TO_SAR, key_price_usd=1.63):
    """Calculates total price for DMMarket keys and returns a tuple (total_sar, total_usd, total_uah)."""
    price_without_fee = number_of_keys * key_price_usd
    fee_usd = round((2.35 / 100 * price_without_fee) + 0.25, 2)
    total_usd = round(price_without_fee + fee_usd, 2)
    total_sar = round(total_usd * usd_to_sar, 2)
    total_uah = round((tf2key_price * number_of_keys) / steam_fee, 2)
    return (total_sar, total_usd, total_uah)
# print(f"TF2Key price = {TF2KEY_PRICE}\nYou get in steam = {round(TF2KEY_PRICE * NumberOfKeys / STEAM_FEE,2)} ukrainian\n----------------------------------------")

from price_fetcher import fetch_live_prices, load_cached_prices, save_cached_prices

#ask the user to input the key number then the price ethier in ryal or ukraiinian then give him the amount of keys and the prices


#1- get the number of keys or do 2
#2- i give you the game price , the program gives you the the prices from the stores and how much you will gain in steam and how much do you require to spend in ryal
if __name__ == "__main__":
    SUPPORTED_CURRENCIES = {
        "1": ("UAH", 18, "₴"),
        "2": ("USD", 1, "$"),
        "3": ("EUR", 3, "€"),
        "4": ("GBP", 2, "£"),
        "5": ("TRY", 17, "TL"),
        "6": ("SAR", 32, "SR"),
        "7": ("RUB", 5, "p")
    }

    print("Select Steam Wallet Currency:")
    print(" (1) UAH ₴ [Default]")
    print(" (2) USD $")
    print(" (3) EUR €")
    print(" (4) GBP £")
    print(" (5) TRY TL")
    print(" (6) SAR SR")
    print(" (7) RUB p")

    curr_input = input("Enter choice (1-7) [default: 1]: ").strip()
    curr_code, curr_id, curr_symbol = SUPPORTED_CURRENCIES.get(curr_input, ("UAH", 18, "₴"))

    cached_data = load_cached_prices()
    use_cache = False

    if cached_data and cached_data.get("currency_id") == curr_id:
        cache_ts = cached_data.get("timestamp", "unknown time")
        cache_prices = cached_data.get("prices", {})
        print(f"\n[i] Found cached prices from {cache_ts}:")
        print(f"    MannCo: ${cache_prices.get('mannco_usd')} | DMarket: ${cache_prices.get('dmarket_usd')} | Steam: {cache_prices.get('steam_uah')} {curr_code}")
        refetch_ans = input("Re-fetch live prices from web? (y/N): ").strip().lower()
        if refetch_ans not in ["y", "yes"]:
            use_cache = True
            live_prices = cache_prices

    if not use_cache:
        live_prices = fetch_live_prices(currency_id=curr_id)
        save_cached_prices(live_prices, currency_code=curr_code, currency_id=curr_id)

    mannco_key_usd = live_prices['mannco_usd']
    dmarket_key_usd = live_prices['dmarket_usd']
    steam_key_price = live_prices['steam_uah']
    TF2KEY_PRICE = steam_key_price

    print(f"\n[+] Active Prices Loaded: MannCo ${mannco_key_usd} | DMMarket ${dmarket_key_usd} | Steam {steam_key_price} {curr_code}\n")

    while True:
        flagway = input("Choose (0) for game price (1) for keys number (q to quit): ").strip().lower()
        if flagway in ["q", "quit", "exit"]:
            print("Exiting calculator.")
            break
        elif flagway == "0":
            try:
                gameprice = float(input(f"Enter the game price ({curr_code}): "))
                net_steam_per_key = TF2KEY_PRICE / STEAM_FEE
                NumberOfKeys = math.ceil(gameprice / net_steam_per_key) 
                mannco_sar, mannco_usd, mannco_steam = calculate_mannco_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=mannco_key_usd)
                dm_sar, dm_usd, dm_steam = calculate_dmmarket_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=dmarket_key_usd)
                print(f"\nKeys needed: {NumberOfKeys}")
                print(f"Mannco (Key price: ${mannco_key_usd}): {mannco_sar} SAR | {mannco_usd} USD |\n you will get in steam account {mannco_steam} {curr_code}")
                print(f"DMMarket (Key price: ${dmarket_key_usd}): {dm_sar} SAR | {dm_usd} USD |\n you will get in steam account {dm_steam} {curr_code}\n")
            except ValueError:
                print("[!] Invalid price input. Please enter a valid number.\n")
        elif flagway == "1":
            try:
                NumberOfKeys = int(input("Enter the number of keys: "))
                mannco_sar, mannco_usd, mannco_steam = calculate_mannco_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=mannco_key_usd)
                dm_sar, dm_usd, dm_steam = calculate_dmmarket_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=dmarket_key_usd)
                print(f"\nMannco (Key price: ${mannco_key_usd}): {mannco_sar} SAR | {mannco_usd} USD |\n you will get in steam account {mannco_steam} {curr_code}")
                print(f"DMMarket (Key price: ${dmarket_key_usd}): {dm_sar} SAR | {dm_usd} USD |\n you will get in steam account {dm_steam} {curr_code}\n")
            except ValueError:
                print("[!] Invalid number of keys. Please enter a valid integer.\n")
        else:
            print("[!] Invalid choice. Please select 0, 1, or q.\n")

