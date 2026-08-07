#Calculation the vlaue of tf2 key price from website and then the sell price in steam and the actual value you got to your account so you convert from ukraine to ryal saudi
import math
import requests
# def get_steam_price_uah():
#     """Fetches the lowest market price for a TF2 Key in Ukrainian Hryvnia (Currency 18)."""
#     url = "https://steamcommunity.com/market/priceoverview/"
#     params = {
#         "appid": 440,
#         "market_hash_name": "Mann Co. Supply Crate Key",
#         "currency": 18
#     }
#     # A standard User-Agent prevents basic HTTP 403 blocks from Steam's edge nodes
#     headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    
#     try:
#         response = requests.get(url, params=params, headers=headers, timeout=5)
#         response.raise_for_status()
#         data = response.json()
        
#         if data.get("success"):
#             # The API returns localized strings (e.g., "100,50₴"). 
#             # We must sanitize the string to cast it to a floating-point number.
#             raw_price = data.get("lowest_price", "0")
#             clean_price = raw_price.replace("₴", "").replace(",", ".").replace(" ", "")
#             return float(clean_price)
            
#     except requests.RequestException as e:
#         print(f"[!] Steam API Error: {e}")
        
#     return 101.00 # Fallback constant


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

from price_fetcher import fetch_live_prices

#ask the user to input the key number then the price ethier in ryal or ukraiinian then give him the amount of keys and the prices


#1- get the number of keys or do 2
#2- i give you the game price , the program gives you the the prices from the stores and how much you will gain in steam and how much do you require to spend in ryal
if __name__ == "__main__":
    live_prices = fetch_live_prices()
    mannco_key_usd = live_prices['mannco_usd']
    dmarket_key_usd = live_prices['dmarket_usd']
    steam_key_uah = live_prices['steam_uah']
    TF2KEY_PRICE = steam_key_uah

    print(f"\n[+] Active Prices Loaded: MannCo ${mannco_key_usd} | DMMarket ${dmarket_key_usd} | Steam {steam_key_uah} UAH\n")

    NumberOfKeys = 1 #number of key you want to buy
    print(f"Number of keys ={NumberOfKeys}\n")

    mannco_sar, mannco_usd, mannco_uah = calculate_mannco_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=mannco_key_usd)
    dm_sar, dm_usd, dm_uah = calculate_dmmarket_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=dmarket_key_usd)

    print(f"Mannco: {mannco_sar} SAR | {mannco_usd} USD |\n you will get in steam account {mannco_uah} UAH")
    print(f"DMMarket: {dm_sar} SAR | {dm_usd} USD |\n you will get in steam account {dm_uah} UAH")

    flagway = input("Choose (0) for game price (1) for keys number: ")

    if flagway == "0":
        gameprice = float(input("Enter the game price: "))
        NumberOfKeys = math.ceil(gameprice / TF2KEY_PRICE) 
        mannco_sar, mannco_usd, mannco_uah = calculate_mannco_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=mannco_key_usd)
        dm_sar, dm_usd, dm_uah = calculate_dmmarket_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=dmarket_key_usd)
        print(f"\nKeys needed: {NumberOfKeys}")
        print(f"Mannco: {mannco_sar} SAR | {mannco_usd} USD | {mannco_uah} UAH")
        print(f"DMMarket: {dm_sar} SAR | {dm_usd} USD | {dm_uah} UAH")
    else:
        NumberOfKeys = int(input("Enter the number of keys: "))

        mannco_sar, mannco_usd, mannco_uah = calculate_mannco_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=mannco_key_usd)
        dm_sar, dm_usd, dm_uah = calculate_dmmarket_price(NumberOfKeys, tf2key_price=TF2KEY_PRICE, key_price_usd=dmarket_key_usd)
        print(f"\nMannco: {mannco_sar} SAR | {mannco_usd} USD |\n you will get in steam account {mannco_uah} UAH")
        print(f"DMMarket: {dm_sar} SAR | {dm_usd} USD |\n you will get in steam account {dm_uah} UAH")

