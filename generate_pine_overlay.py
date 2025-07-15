import json
import requests
import os

ZONES_FILE = "sniper-strike-zones.json"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1394792542608035920/pVJ9YIo8zfjRa9hxrJzEr7RnuWTKb7fE--2SkdDw2AatCf3BH5AVkcI04u6VIy6mOAYM"

def generate_and_post_pine_overlay():
    if not os.path.exists(ZONES_FILE):
        print("❌ File not found:", ZONES_FILE)
        return

    with open(ZONES_FILE) as f:
        zones = json.load(f)

    prices = sorted({round(float(z['price']), 1) for z in zones})
    array_str = "[" + ", ".join(map(str, prices)) + "]"

    pine_code = f"""//@version=5
indicator("Sniper Zones", overlay=true)
zones = array.fromlist({array_str})

for i = 0 to array.size(zones) - 1
    price = array.get(zones, i)
    line.new(bar_index, price, bar_index + 50, price, color=color.red, style=line.style_dotted)
"""

    payload = {
        "username": "Pine Sync Bot",
        "content": f"📈 **Sniper Zone Overlay Update**\n```pine\n{pine_code[:1900]}\n```"
    }

    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print("✅ Pine overlay posted.")
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")

if __name__ == "__main__":
    generate_and_post_pine_overlay()
