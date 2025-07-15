import os
import requests
import time
from options_wall_filter import is_valid_wall
from trap_logger import save_trap, is_repeated_trap

# Deribit API endpoints
INSTRUMENTS_API = "https://www.deribit.com/api/v2/public/get_instruments"
BOOK_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"

# Discord webhook from environment
WEBHOOK_URL = os.getenv("DISCORD_OPTIONS_WEBHOOK")

# Fetch live BTC options from Deribit
def get_live_btc_option_symbols():
    try:
        response = requests.get(INSTRUMENTS_API, params={
            "currency": "BTC",
            "kind": "option",
            "expired": "false"
        })
        data = response.json().get("result", [])
        return [item["instrument_name"] for item in data]
    except Exception as e:
        print(f"[ERROR] Failed to load instruments: {e}")
        return []

# Fetch OI, volume, and price for a given symbol
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

# Send alert to Discord, tag repeated walls
def post_alert(data, repeat=False):
    tag = "⚠️ Repeated Wall" if repeat else ""
    payload = {
        "username": "Deribit Options Bot",
        "embeds": [{
            "title": f"📊 Deribit BTC Option Wall {tag}",
            "description": f"**{data['symbol']}**\nOI: `{data['open_interest']}`\nVolume: `{data['volume']}`\nLast: `{data['last']}`",
            "color": 15158332 if repeat else 5814783
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"[ERROR] Failed to post to Discord: {e}")

# Main loop: scan, filter, alert, log
def run_scanner():
    print("[+] Scanning Deribit Options Walls...")
    symbols = get_live_btc_option_symbols()
    for symbol in symbols:
        if "-C" in symbol or "-P" in symbol:
            data = fetch_option_wall(symbol)
            if data and is_valid_wall(data):
                repeat = is_repeated_trap(data["symbol"])
                post_alert(data, repeat=repeat)
                save_trap(data)
            time.sleep(0.25)  # Rate limit buffer

if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(300)  # Run every 5 minutes
