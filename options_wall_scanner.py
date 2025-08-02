import os
import time
import requests

from options_wall_filter import is_valid_wall
from trap_logger import save_trap, is_repeated_trap
from strike_cluster import detect_clusters, is_cluster_strike, extract_strike
from cluster_memory import save_cluster_strike, is_repeated_cluster
from heatmap_builder import build_heatmap
from sniper_score_engine import score_strike
from rsi_sniper_confluence import is_high_confluence_sniper
from options_wall_memory_tracker import update_wall_memory

WEBHOOK_DEFAULT = "https://discord.com/api/webhooks/1393246400275546352/qao3Rw8BaDDlONOV3zp0_zfYEpNiIRXrEZ-UAGFAMcxK0FT_oJXHkFkic4RenmOUe-4Q"
WEBHOOK_SNIPER = "https://discord.com/api/webhooks/1394793236932857856/10d2BO33Ckf2ouUQ5ClrnZpbxmzsmERA0SzEEkIwvJe1Rq5GGn0LWLS3vRqTOHwd_Qqc"

INSTRUMENTS_API = "https://www.deribit.com/api/v2/public/get_instruments"
BOOK_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"


def get_live_btc_option_symbols():
    try:
        response = requests.get(INSTRUMENTS_API, params={
            "currency": "BTC", "kind": "option", "expired": "false"
        })
        return [item["instrument_name"] for item in response.json().get("result", [])]
    except Exception as e:
        print(f"[ERROR] Loading instruments: {e}")
        return []


def fetch_option_wall(symbol):
    try:
        response = requests.get(BOOK_API, params={"instrument_name": symbol})
        result = response.json().get("result", [{}])[0]
        return {
            "symbol": symbol,
            "open_interest": result.get("open_interest", 0),
            "volume": result.get("volume", 0),
            "last": result.get("last_price", 0)
        }
    except Exception as e:
        print(f"[ERROR] Fetching {symbol}: {e}")
        return None


def post_alert(data, tags, score, webhook_url):
    title = "📊 Deribit BTC Option Wall " + " ".join(tags)
    color = 16734296 if score >= 5 else 15158332 if "⚠️ Repeated Wall" in tags else 5814783

    payload = {
        "username": "Deribit Options Bot",
        "embeds": [{
            "title": title,
            "description": f"**{data['symbol']}**\nOI: `{data['open_interest']}`\nVolume: `{data['volume']}`\nLast: `{data['last']}`",
            "color": color
        }]
    }
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"[ERROR] Posting to Discord: {e}")


def run_scanner():
    print("[+] Scanning Deribit Options Walls...")
    symbols = get_live_btc_option_symbols()
    valid_walls = []

    for symbol in symbols:
        if "-C" in symbol or "-P" in symbol:
            data = fetch_option_wall(symbol)
            if data and is_valid_wall(data):
                valid_walls.append(data)
            time.sleep(0.25)

    cluster_strikes = detect_clusters(valid_walls)

    current_price = sum([w["last"] for w in valid_walls if w["last"] > 0]) / max(1, len(valid_walls))
    update_wall_memory(valid_walls, current_price)

    for strike in cluster_strikes:
        save_cluster_strike(strike)
    build_heatmap()

    for data in valid_walls:
        strike = extract_strike(data["symbol"])
        is_repeat = is_repeated_trap(data["symbol"])
        is_cluster = is_cluster_strike(data["symbol"], cluster_strikes)
        is_cluster_repeat = is_repeated_cluster(strike) if is_cluster else False
        score = score_strike(data)
        sniper_ready = is_high_confluence_sniper(data["symbol"])

        tags = []
        if is_repeat or is_cluster_repeat:
            tags.append("⚠️ Repeated Wall")
        if is_cluster:
            tags.append("🎯 Cluster Strike")
        if score >= 5:
            tags.append(f"🔥 Score: {score}")
        elif score >= 2:
            tags.append(f"⭐ Score: {score}")
        if sniper_ready:
            tags.append("🧠 RSI + Options")

        webhook = WEBHOOK_SNIPER if sniper_ready else WEBHOOK_DEFAULT
        post_alert(data, tags, score, webhook)
        save_trap(data)


if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(300)
