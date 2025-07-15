import json
import os
from datetime import datetime

LOG_FILE = "trap_memory.json"

# Save trap to memory
def save_trap(data):
    trap = {
        "symbol": data["symbol"],
        "oi": data["open_interest"],
        "volume": data["volume"],
        "last": data["last"],
        "timestamp": datetime.utcnow().isoformat()
    }

    # Load existing
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = []

    memory.append(trap)

    with open(LOG_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Optional: Load for comparison
def load_traps():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []
