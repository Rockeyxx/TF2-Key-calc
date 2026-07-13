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


NumberOfKeys = 1 #number of key you want to buy
print(f"Number of keys ={NumberOfKeys}\n")

#Mannco Section
TF2KEY_PRICEMA = 1.73 #dollar
MANNCO_FEE = round(0.06275 * NumberOfKeys + 0.305,2)

Total_price_after_feeMA = MANNCO_FEE + TF2KEY_PRICEMA * NumberOfKeys
print(f"Mannco\nTF2Key price ={TF2KEY_PRICEMA}\nFee price ={MANNCO_FEE} \nTotal Price ={Total_price_after_feeMA}\nSaudi Riyal={round(Total_price_after_feeMA*3.75,2)}\n----------------------------------------")

#Dmmarket section
TF2KEY_PRICEDM = 1.73 #dollar
price_without_fee = NumberOfKeys * TF2KEY_PRICEDM
DMMARKET_FEE = round((2.35/100 * price_without_fee) + 0.25,2)
test = 1.73 *0.0235 + 0.25
Total_price_after_feeDM = price_without_fee + DMMARKET_FEE
print(f"Dmmarket\nTF2Key price ={TF2KEY_PRICEDM}\nFee price ={DMMARKET_FEE} \nTotal Price ={Total_price_after_feeDM}\nSaudi Riyal ={round(Total_price_after_feeDM*3.75,2)}\n----------------------------------------")

#Steam section
TF2KEY_PRICE = 101 #get_steam_price_uah() #UKRAININ 
STEAM_FEE = 1.15
print(f"TF2Key price = {TF2KEY_PRICE}\nYou get in steam = {round(TF2KEY_PRICE * NumberOfKeys / STEAM_FEE,2)} ukrainian\n----------------------------------------")

