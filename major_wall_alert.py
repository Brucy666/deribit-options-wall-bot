import requests
from datetime import datetime

WEBHOOK_MAJOR_WALLS = "https://discord.com/api/webhooks/1393246400275546352/qao3Rw8BaDDlONOV3zp0_zfYEpNiIRXrEZ-UAGFAMcxK0FT_oJXHkFkic4RenmOUe-4Q"

def post_major_wall_alert(call_wall, put_wall, current_price):
    fields = []

    if call_wall:
        fields.append({
            "name": "🟢 Largest Call Wall (Above Price)",
            "value": f"Strike: `{call_wall['strike']}`\nOI: `{call_wall['oi']}`\nSeen: `{call_wall['seen_count']}x`",
            "inline": False
        })

    if put_wall:
        fields.append({
            "name": "🔴 Largest Put Wall (Below Price)",
            "value": f"Strike: `{put_wall['strike']}`\nOI: `{put_wall['oi']}`\nSeen: `{put_wall['seen_count']}x`",
            "inline": False
        })

    fields.append({
        "name": "📍 Spot Price",
        "value": f"${current_price:,.2f}",
        "inline": False
    })

    embed = {
        "title": f"🧱 Major Option Walls — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "fields": fields,
        "color": 15844367
    }

    payload = {
        "username": "Options Wall Bot",
        "embeds": [embed]
    }

    try:
        requests.post(WEBHOOK_MAJOR_WALLS, json=payload)
        print("[✓] Major wall alert sent to Discord.")
    except Exception as e:
        print(f"[ERROR] Failed to post major wall alert: {e}")
