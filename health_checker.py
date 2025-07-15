import os
import json
from datetime import datetime

def check_file(path):
    if os.path.exists(path):
        mod_time = os.path.getmtime(path)
        return datetime.utcfromtimestamp(mod_time).isoformat()
    return "❌ Not Found"

def system_health_report():
    print("📊 SYSTEM HEALTH CHECK\n")

    files = [
        "trap_memory.json",
        "cluster_memory.json",
        "cluster_heatmap.json",
        "sniper-strike-zones.json",
        "top_strikes_report.txt"
    ]

    for f in files:
        print(f"{f:30} → Last updated: {check_file(f)}")

    # Bonus: print cluster count
    if os.path.exists("cluster_memory.json"):
        with open("cluster_memory.json") as f:
            data = json.load(f)
            print(f"Total Cluster Logs: {len(data)}")

    if os.path.exists("cluster_heatmap.json"):
        with open("cluster_heatmap.json") as f:
            data = json.load(f)
            top = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
            print("Top Zones by Frequency:")
            for k, v in top:
                print(f"  → {k}: {v} hits")
