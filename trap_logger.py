import json
import os
from datetime import datetime

LOG_FILE = "trap_memory.json"

# Save trap to local memory
def save_trap(data):
    trap = {
        "symbol": data["symbol"],
        "oi": data["open_interest"],
        "volume": data["volume"],
        "last": data["last"],
        "timestamp": datetime.utcnow().isoformat()
    }

    # Load existing trap memory
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = []

    memory.append(trap)

    with open(LOG_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Check if the wall has appeared before
def is_repeated_trap(symbol):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            memory = json.load(f)
        return any(trap["symbol"] == symbol for trap in memory)
    return False
