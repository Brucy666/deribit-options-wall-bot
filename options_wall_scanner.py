import requests
import time
import json

DERIBIT_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"
INSTRUMENTS = [
    "BTC-14JUL23-30000-C",
    "BTC-14JUL23-29000-P",
    "BTC-21JUL23-31000-C",
    "BTC-21JUL23-28000-P",
    # Add more relevant calls and puts
]

WEBHOOK_URL = os.getenv("DISCORD_OPTIONS_WEBHOOK")

def fetch_option_wall(symbol):
    try:
        response = requests.get(DERIBIT_API, params={"instrument_name": symbol})
        data = response.json()["result"][0]
        return {
            "symbol": symbol,
            "open_interest": data["open_interest"] or 0,
            "volume": data["volume"] or 0,
            "last": data["last"] or 0,
        }
    except Exception as e:
        print(f"Failed to fetch {symbol}: {e}")
        return None

def scan_option_walls():
    for symbol in INSTRUMENTS:
        data = fetch_option_wall(symbol)
        if not data:
            continue

        score = 0
        if data["open_interest"] > 100:
            score += 1
        if data["volume"] > 50:
            score += 1

        if score >= 2:
            post_alert(data)

def post_alert(data):
    payload = {
        "username": "Deribit Options Bot",
        "embeds": [
            {
                "title": "🟣 Options Wall Detected",
                "description": f"**Symbol:** {data['symbol']}\n**Open Interest:** {data['open_interest']}\n**Volume:** {data['volume']}\n**Last Price:** {data['last']}",
                "color": 10070709  # Purple
            }
        ]
    }
    try:
        requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    except Exception as e:
        print(f"Webhook error: {e}")

if __name__ == "__main__":
    while True:
        print("[+] Scanning Deribit Options Walls...")
        scan_option_walls()
        time.sleep(60)
