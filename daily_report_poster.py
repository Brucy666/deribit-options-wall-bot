import os
import requests
from top_strikes_report import generate_top_strike_report

WEBHOOK_URL = "https://discord.com/api/webhooks/1394793145400823909/ny0lkqtyJ1rfs1Zf2LPN2s_Ln9CWGC02mF4ltzzsMtd7RSgMBNalvXp17PwYfSVF4tFr"
REPORT_FILE = "top_strikes_report.txt"

def post_daily_report():
    generate_top_strike_report()

    if not os.path.exists(REPORT_FILE):
        print("❌ Report not found.")
        return

    with open(REPORT_FILE, "r") as f:
        content = f.read()

    payload = {
        "username": "Sniper Report Bot",
        "content": f"📊 **Daily Top Sniper Strikes**\n```{content[:1900]}```"
    }

    try:
        requests.post(WEBHOOK_URL, json=payload)
        print("✅ Report posted to Discord.")
    except Exception as e:
        print(f"[ERROR] Failed to post report: {e}")

if __name__ == "__main__":
    post_daily_report()
