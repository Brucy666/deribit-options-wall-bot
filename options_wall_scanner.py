import os
import requests
import time

# Deribit API endpoints
INSTRUMENTS_API = "https://www.deribit.com/api/v2/public/get_instruments"
BOOK_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"

# Discord webhook
WEBHOOK_URL = os.getenv("DISCORD_OPTIONS_WEBHOOK")

# Load live BTC option instruments
def get_live_btc_option_symbols():
    try:
        response = requests.get(INSTRUMENTS_API, params={
            "currency": "BTC",
            "kind": "option",
            "expired": "false"
        })
        data = response.json().get("result", [])
        symbols = [item["instrument_name"] for item in data]
        return symbols
    except Exception as e:
        print(f"[ERROR] Failed to load instruments: {e}")
        return []

# Fetch OI, volume, and last price for a given option
def fetch_option_wall(symbol):
    try:
        response = requests.get(BOOK_API, params={"instrument_name": symbol})
        result = response.json().get("result")
        if not result:
            print(f"[!] No result for {symbol}")
            return None
        data = result[0]
        return {
            "symbol": symbol,
            "open_interest": data.get("open_interest", 0),
            "volume": data.get("volume", 0),
            "last": data.get("last_price", 0)
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch {symbol}: {e}")
        return None

# Send formatted alert to Discord
def post_alert(data):
    payload = {
        "username": "Deribit Options Bot",
        "embeds": [{
            "title": f"📊 Deribit BTC Option Wall",
            "description": f"**{data['symbol']}**\nOI: `{data['open_interest']}`\nVolume: `{data['volume']}`\nLast: `{data['last']}`",
            "color": 5814783
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"[ERROR] Failed to post to Discord: {e}")

# Main loop
def run_scanner():
    print("[+] Scanning Deribit Options Walls...")
    symbols = get_live_btc_option_symbols()
    for symbol in symbols:
        if "-C" in symbol or "-P" in symbol:  # Optional: skip some
            data = fetch_option_wall(symbol)
            if data and data["open_interest"] > 0:
                post_alert(data)
            time.sleep(0.25)  # Rate limit

if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(300)  # Scan every 5 minutes
