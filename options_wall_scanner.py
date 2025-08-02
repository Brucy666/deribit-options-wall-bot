import time
import requests
from datetime import datetime, timezone

from options_wall_filter import is_valid_wall
from trap_logger import save_trap, is_repeated_trap
from strike_cluster import detect_clusters, is_cluster_strike, extract_strike
from cluster_memory import save_cluster_strike, is_repeated_cluster
from heatmap_builder import build_heatmap
from sniper_score_engine import score_strike
from rsi_sniper_confluence import is_high_confluence_sniper
from options_wall_memory_tracker import update_wall_memory
from options_sniper_export import export_sniper_wall_snapshot
from options_wall_bias_engine import score_wall_bias
from options_discord_summary_builder import build_wall_summary
from options_trap_detector import detect_trap_wall
from major_wall_detector import get_major_call_put_walls  # ✅ new

# Discord webhooks
WEBHOOK_DEFAULT = "https://discord.com/api/webhooks/1393246400275546352/qao3Rw8BaDDlONOV3zp0_zfYEpNiIRXrEZ-UAGFAMcxK0FT_oJXHkFkic4RenmOUe-4Q"
WEBHOOK_SNIPER = "https://discord.com/api/webhooks/1394793236932857856/10d2BO33Ckf2ouUQ5ClrnZpbxmzsmERA0SzEEkIwvJe1Rq5GGn0LWLS3vRqTOHwd_Qqc"

INSTRUMENTS_API = "https://www.deribit.com/api/v2/public/get_instruments"
BOOK_API = "https://www.deribit.com/api/v2/public/get_book_summary_by_instrument"

def get_live_btc_option_symbols():
    try:
        res = requests.get(INSTRUMENTS_API, params={"currency": "BTC", "kind": "option", "expired": "false"})
        return [x["instrument_name"] for x in res.json().get("result", [])]
    except Exception as e:
        print(f"[ERROR] get_live_btc_option_symbols: {e}")
        return []

def fetch_option_wall(symbol):
    try:
        res = requests.get(BOOK_API, params={"instrument_name": symbol})
        result = res.json().get("result", [{}])[0]
        parts = symbol.split("-")
        if len(parts) != 4:
            return None
        return {
            "symbol": symbol,
            "strike": float(parts[2]),
            "type": parts[3],
            "expiry": parts[1],
            "open_interest": result.get("open_interest", 0),
            "volume": result.get("volume", 0),
            "last": result.get("last_price", 0)
        }
    except Exception as e:
        print(f"[ERROR] fetch_option_wall({symbol}): {e}")
        return None

def post_alert(wall, tags, score, webhook):
    title = "📊 Deribit BTC Option Wall " + " ".join(tags)
    color = 16734296 if score >= 5 else 15158332 if "⚠️ Repeated Wall" in tags else 5814783

    payload = {
        "username": "Deribit Options Bot",
        "embeds": [{
            "title": title,
            "description": (
                f"**{wall['symbol']}**\n"
                f"OI: `{wall['open_interest']}`\n"
                f"Volume: `{wall['volume']}`\n"
                f"Last: `{wall['last']}`"
            ),
            "color": color
        }]
    }
    try:
        print(f"[POST] Alerting {wall['symbol']} Tags: {tags}")
        requests.post(webhook, json=payload)
    except Exception as e:
        print(f"[ERROR] Discord post failed: {e}")

def run_scanner():
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Scanning Deribit Options Walls...")
    symbols = get_live_btc_option_symbols()
    valid_walls = []

    for symbol in symbols:
        if "-C" in symbol or "-P" in symbol:
            wall = fetch_option_wall(symbol)
            if wall:
                print("[DEBUG] WALL:", wall)
                valid_walls.append(wall)
            time.sleep(0.25)

    if not valid_walls:
        print("[!] No valid walls found.")
        return

    cluster_strikes = detect_clusters(valid_walls)
    current_price = sum([w["last"] for w in valid_walls if w["last"] > 0]) / max(1, len(valid_walls))

    wall_memory = update_wall_memory(valid_walls, current_price)
    export_sniper_wall_snapshot(valid_walls, wall_memory, current_price)
    build_wall_summary(current_price, wall_memory)
    bias_report = score_wall_bias(current_price, wall_memory)

    # ✅ Major wall detection
    major = get_major_call_put_walls(wall_memory, current_price)
    if major["call"]:
        print(f"🟢 CALL Wall: {major['call']['strike']} | OI: {major['call']['oi']:.1f}")
    if major["put"]:
        print(f"🔴 PUT Wall:  {major['put']['strike']} | OI: {major['put']['oi']:.1f}")

    for strike in cluster_strikes:
        save_cluster_strike(strike)
    build_heatmap()

    for wall in valid_walls:
        strike = extract_strike(wall["symbol"])
        is_repeat = is_repeated_trap(wall["symbol"])
        is_cluster = is_cluster_strike(wall["symbol"], cluster_strikes)
        is_cluster_repeat = is_repeated_cluster(strike) if is_cluster else False
        score = score_strike(wall)
        sniper_ready = is_high_confluence_sniper(wall["symbol"])

        rsi_fast = 67
        rsi_slow = 65
        trap = detect_trap_wall(wall, wall_memory, current_price, rsi_fast, rsi_slow)

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
        if trap["is_trap"]:
            tags.append("🚨 Trap Risk")
            print("[TRAP]", trap["reason"])
        if bias_report["bias"] == "bullish":
            tags.append("🟢 Bullish Bias")
        elif bias_report["bias"] == "bearish":
            tags.append("🔴 Bearish Bias")
        elif bias_report["bias"] == "trap_zone":
            tags.append("⚠️ Trap Zone")

        if not tags:
            tags.append("🔍 TEST MODE")

        webhook = WEBHOOK_SNIPER if sniper_ready else WEBHOOK_DEFAULT
        post_alert(wall, tags, score, webhook)
        save_trap(wall)

if __name__ == "__main__":
    while True:
        run_scanner()
        time.sleep(300)
