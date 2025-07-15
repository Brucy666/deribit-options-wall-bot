import os
import requests
import time

from options_wall_filter import is_valid_wall
from trap_logger import save_trap, is_repeated_trap
from strike_cluster import (
    detect_clusters,
    is_cluster_strike,
    extract_strike
)
from cluster_memory import save_cluster_strike, is_repeated_cluster

# Deribit API endpoints
INSTRUMENTS_API = "https://www.deribit.com/api/v2/public/get_instruments"
BOOK_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"

# Discord webhook
WEBHOOK_URL = os.getenv("DISCORD_OPTIONS_WEBHOOK")

# Fetch BTC option symbols
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

# Fetch market data for an instrument
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

# Send alert to Discord
def post_alert(data, repeat=False, cluster=False):
    tags = []
    if repeat:
        tags.append("⚠️ Repeated Wall")
    if cluster:
        tags.append("🎯 Cluster Strike")

    title = "📊 Deribit BTC Option Wall"
    if tags:
        title += " " + " ".join(tags)

    payload = {
        "username": "Deribit Options Bot",
        "embeds": [{
            "title": title,
            "description": f"**{data['symbol']}**\nOI: `{data['open_interest']}`\nVolume: `{data['volume']}`\nLast: `{data['last']}`",
            "color": 15158332 if repeat or cluster else 5814783
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
    valid_walls = []

    # Gather filtered walls
    for symbol in symbols:
        if "-C" in symbol or "-P" in symbol:
            data = fetch_option_wall(symbol)
            if data and is_valid_wall(data):
                valid_walls.append(data)
            time.sleep(0.25)

    # Detect and store cluster zones
    cluster_strikes = detect_clusters(valid_walls)
    for c in cluster_strikes:
        save_cluster_strike(c)

    # Post alerts
    for data in valid_walls:
        strike = extract_strike(data["symbol"])
        is_repeat = is_repeated_trap(data["symbol"])
        is_cluster = is_cluster_strike(data["symbol"], cluster_strikes)
        is_cluster_repeat = is_repeated_cluster(strike) if is_cluster else False

        post_alert(data, repeat=(is_repeat or is_cluster_repeat), cluster=is_cluster)
        save_trap(data)

if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(300)
