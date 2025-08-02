from datetime import datetime

# In-memory store of seen walls
wall_memory = {}

def update_wall_memory(walls, current_price):
    """
    Updates memory store with newly scanned walls.
    Tracks open interest, strike, type, and how many times seen.
    """
    global wall_memory
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    for wall in walls:
        # ✅ Safety: ensure it's a valid dict with required keys
        if not isinstance(wall, dict) or not all(k in wall for k in ["strike", "type", "expiry", "open_interest"]):
            print("[SKIP] Malformed wall:", wall)
            continue

        try:
            strike = float(wall["strike"])
            opt_type = wall["type"]
            expiry = wall["expiry"]
            oi = float(wall["open_interest"])
        except Exception as e:
            print(f"[ERROR] Parsing wall: {e}")
            continue

        key = f"{strike}-{opt_type}-{expiry}"

        if key not in wall_memory:
            wall_memory[key] = {
                "strike": strike,
                "type": opt_type,
                "expiry": expiry,
                "seen_count": 1,
                "oi": oi,
                "last_seen": now,
                "first_seen": now,
                "last_price": current_price
            }
        else:
            wall_memory[key]["seen_count"] += 1
            wall_memory[key]["last_seen"] = now
            wall_memory[key]["oi"] = oi
            wall_memory[key]["last_price"] = current_price

        print(f"[MEMORY] Seen {key} → x{wall_memory[key]['seen_count']}")

    return wall_memory
