import json
import os
from datetime import datetime

CLUSTER_LOG = "cluster_memory.json"

# Save each cluster strike level
def save_cluster_strike(strike):
    entry = {
        "strike": strike,
        "timestamp": datetime.utcnow().isoformat()
    }

    if os.path.exists(CLUSTER_LOG):
        with open(CLUSTER_LOG, "r") as f:
            memory = json.load(f)
    else:
        memory = []

    memory.append(entry)

    with open(CLUSTER_LOG, "w") as f:
        json.dump(memory, f, indent=2)

# Load all past cluster levels
def load_clusters():
    if os.path.exists(CLUSTER_LOG):
        with open(CLUSTER_LOG, "r") as f:
            return json.load(f)
    return []

# Check if strike is a repeated cluster zone
def is_repeated_cluster(strike):
    memory = load_clusters()
    return any(abs(strike - int(entry["strike"])) <= 50 for entry in memory)
