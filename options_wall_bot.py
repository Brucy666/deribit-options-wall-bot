# deribit_options_bot.py

import requests
import time
import datetime
import json

DERIBIT_API_URL = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"

OPTIONS_SYMBOLS = [
    "BTC-11JUL25-65000-C",
    "BTC-11JUL25-65000-P",
    "BTC-12JUL25-66000-C",
    "BTC-12JUL25-66000-P",
    # Add more live symbols as needed
]

DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_HERE"


def fetch_options_summary(symbol):
    url = f"{DERIBIT_API_URL}?instrument_name={symbol}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("result", [{}])[0]
        else:
            print(f"Failed to fetch {symbol} - {response.status_code}")
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return {}


def format_alert(symbol, data):
    mark_price = data.get("mark_price", 0)
    open_interest = data.get("open_interest", 0)
    volume = data.get("volume", 0)
    timestamp = datetime.datetime.utcnow().isoformat()

    alert = {
        "username": "options bot",
        "embeds": [
            {
                "title": f"📈 Options Alert: {symbol}",
                "color": 0x00cccc,
                "fields": [
                    {"name": "Mark Price", "value": f"${mark_price:.2f}", "inline": True},
                    {"name": "Open Interest", "value": f"{open_interest:.2f}", "inline": True},
                    {"name": "Volume", "value": f"{volume:.2f}", "inline": True},
                    {"name": "Time", "value": timestamp, "inline": False}
                ]
            }
        ]
    }
    return alert


def send_alert(alert):
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=alert)
        if response.status_code != 204:
            print(f"Failed to send alert: {response.text}")
    except Exception as e:
        print(f"Error sending Discord alert: {e}")


def run_bot():
    while True:
        for symbol in OPTIONS_SYMBOLS:
            data = fetch_options_summary(symbol)
            if data:
                alert = format_alert(symbol, data)
                send_alert(alert)
        time.sleep(60)


if __name__ == "__main__":
    run_bot()
