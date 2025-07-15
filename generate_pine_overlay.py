import json
import requests
import os

ZONES_FILE = "sniper-strike-zones.json"
PINE_OUTPUT = "pine_script_overlay.pine"
DISCORD_PINE_WEBHOOK = "https://discord.com/api/webhooks/1394792542608035920/pVJ9YIo8zfjRa9hxrJzEr7RnuWTKb7fE--2SkdDw2AatCf3BH5AVkcI04u6VIy6mOAYM"

def generate_pine_script():
    if not os.path.exists(ZONES_FILE):
        print("❌ sniper-strike-zones.json not found.")
        return

    with open(ZONES_FILE) as f:
        zones = json.load(f)

    prices = sorted(set(round(float(z['price']), 1) for z in zones))
    array_str = "[" + ", ".join(str(p) for p in prices) + "]"

    pine_code = f"""//@version=5
indicator("Sniper Zones", overlay=true)
zones = array.fromlist({array_str})

for i = 0 to array.size(zones) - 1
    price = array.get(zones, i)
    line.new(bar_index, price, bar_index + 50, price, color=color.red, style=line.style_dotted)
"""

    with open(PINE_OUTPUT, "w") as f:
        f.write(pine_code)

    post_to_discord(pine_code)

def post_to_discord(script_text):
    payload = {
        "username": "Pine Sync Bot",
        "content": "📈 **Updated TradingView Pine Overlay:**\n```pine\n" + script_text[:1900] + "\n```"
    }
    try:
        requests.post(DISCORD_PINE_WEBHOOK, json=payload)
        print("✅ Pine overlay posted to Discord.")
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")

if __name__ == "__main__":
    generate_pine_script()

