import json
import os
from datetime import datetime

EXPORT_FILE = "sniper_wall_output.json"

def export_sniper_wall_snapshot(current_walls, wall_memory, price):
    """
    Export walls near current price into a sniper-readable file.
    """

    active_call_walls = []
    active_put_walls = []

    for wall in current_walls:
        distance_pct = abs(price - wall["strike"]) / price
        if distance_pct <= 0.02:  # Within 2% of current price
            record = {
                "strike": wall["strike"],
                "type": wall["type"],
                "expiry": wall["expiry"],
                "oi": wall["oi"],
                "volume": wall["volume"],
                "seen_count": wall_memory.get(f"{wall['strike']}-{wall['type']}-{wall['expiry']}", {}).get("seen_count", 1)
            }
            if wall["type"] == "C":
                active_call_walls.append(record)
            elif wall["type"] == "P":
                active_put_walls.append(record)

    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "price": price,
        "call_walls": sorted(active_call_walls, key=lambda w: w["strike"]),
        "put_walls": sorted(active_put_walls, key=lambda w: w["strike"], reverse=True)
    }

    with open(EXPORT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)
    return snapshot
