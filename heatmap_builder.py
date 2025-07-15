import json
import os
from collections import defaultdict

CLUSTER_LOG = "cluster_memory.json"
HEATMAP_FILE = "cluster_heatmap.json"

# Build heatmap: strike → count
def build_heatmap():
    if not os.path.exists(CLUSTER_LOG):
        return {}

    with open(CLUSTER_LOG, "r") as f:
        entries = json.load(f)

    counts = defaultdict(int)
    for entry in entries:
        strike = int(entry["strike"])
        counts[strike] += 1

    with open(HEATMAP_FILE, "w") as f:
        json.dump(dict(sorted(counts.items())), f, indent=2)

    return counts

# Load heatmap
def load_heatmap():
    if os.path.exists(HEATMAP_FILE):
        with open(HEATMAP_FILE, "r") as f:
            return json.load(f)
    return {}
