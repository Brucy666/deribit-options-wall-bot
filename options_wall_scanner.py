import os
import requests
import time
import json

DERIBIT_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"

# ✅ Live options (as of 11 July 2025 — weekly, next-week, and monthly)
INSTRUMENTS = [
    "BTC-19JUL24-60000-C",
    "BTC-19JUL24-50000-P",
    "BTC-26JUL24-65000-C",
    "BTC-26JUL24-47000-P",
    "BTC-30AUG24-70000-C",
    "BTC-30AUG24-45000-P",
]

WEBHOOK_URL = os.getenv("DISCORD_OPTIONS_WEBHOOK")

def fetch_option_wall(symbol):
    try:
        response = requests.get(DERIBIT_API, params={"instrument_name": symbol})
        data = response.json()["result"][0]
        return {
            "symbol": symbol,
            "open_interest": data.get("open_interest", 0),
            "volume": data.get("volume", 0),
            "last": data.get("last", 0)
        }
    except Exception as e:
        print(f"Failed to fetch {symbol}: {e}")
        return None

def post_alert(data):
    payload = {
        "username": "Deribit Options Bot",
        "embeds": [
            {
                "title": "🟣 Options Wall Detected",
                "description": (
                    f"**Symbol:** `{data['symbol']}`\n"
                    f"**Open Interest:** `{data['open_interest']}`\n"
                    f"**Volume:** `{data['volume']}`\n"
                    f"**Last Price:** `{data['last']}`"
                ),
                "color": 10070709  # Purple
            }
        ]
    }
    try:
        requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    except Exception as e:
        print(f"Webhook error: {e}")

def scan_option_walls():
    for symbol in INSTRUMENTS:
        data = fetch_option_wall(symbol)
        if not data:
            continue

        # 🧠 Scoring logic
        score = 0
        if data["open_interest"] > 100:
            score += 1
        if data["volume"] > 50:
            score += 1

        if score >= 2:
            post_alert(data)

if __name__ == "__main__":
    while True:
        print("[+] Scanning Deribit Options Walls...")
        scan_option_walls()
        time.sleep(300)  # every 5 minutes
