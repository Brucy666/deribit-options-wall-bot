import requests
from datetime import datetime

WEBHOOK_SUMMARY = "https://discord.com/api/webhooks/1393246400275546352/qao3Rw8BaDDlONOV3zp0_zfYEpNiIRXrEZ-UAGFAMcxK0FT_oJXHkFkic4RenmOUe-4Q"

def build_wall_summary(current_price, wall_memory):
    call_lines = []
    put_lines = []

    for wall in wall_memory.values():
        dist_pct = abs(current_price - wall["strike"]) / current_price * 100
        info = f"{wall['strike']} ({wall['oi']} OI / {wall['seen_count']}x / {dist_pct:.1f}%)"

        if wall["type"] == "C":
            call_lines.append(info)
        elif wall["type"] == "P":
            put_lines.append(info)

    call_summary = "\n".join(sorted(call_lines, reverse=True))
    put_summary = "\n".join(sorted(put_lines))

    embed = {
        "title": f"📊 BTC Option Wall Summary — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "fields": [
            {"name": "📈 Call Walls (Above Price)", "value": call_summary or "None", "inline": False},
            {"name": "📉 Put Walls (Below Price)", "value": put_summary or "None", "inline": False},
            {"name": "📍 Current BTC Price", "value": f"${current_price:,.2f}", "inline": False}
        ],
        "color": 3447003
    }

    payload = {
        "username": "Options Summary Bot",
        "embeds": [embed]
    }

    try:
        requests.post(WEBHOOK_SUMMARY, json=payload)
        print("[✓] Wall summary posted to Discord.")
    except Exception as e:
        print(f"[ERROR] Failed to post summary: {e}")
