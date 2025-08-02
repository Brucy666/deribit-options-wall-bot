import json
import os
from datetime import datetime

MEMORY_FILE = "wall_state.json"

def load_wall_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_wall_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_wall_memory(current_walls, price):
    """
    Updates wall_state.json with current wall info.

    Each wall should be a dict:
    {
        "strike": 49000,
        "type": "C",  # or "P"
        "expiry": "2025-08-15",
        "oi": 5400,
        "volume": 120.5
    }
    """
    memory = load_wall_memory()
    now = datetime.utcnow().isoformat()

    for wall in current_walls:
        key = f"{wall['strike']}-{wall['type']}-{wall['expiry']}"
        if key in memory:
            memory[key]["seen_count"] += 1
            memory[key]["last_seen"] = now
            memory[key]["last_price"] = price
        else:
            memory[key] = {
                "strike": wall["strike"],
                "type": wall["type"],
                "expiry": wall["expiry"],
                "oi": wall["oi"],
                "volume": wall["volume"],
                "first_seen": now,
                "last_seen": now,
                "seen_count": 1,
                "last_price": price
            }

    save_wall_memory(memory)
    return memory
