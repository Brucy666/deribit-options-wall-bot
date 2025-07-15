import json
from collections import defaultdict

CLUSTER_LOG = "cluster_memory.json"
HEATMAP_FILE = "cluster_heatmap.json"
OUTPUT = "top_strikes_report.txt"

def generate_top_strike_report():
    if not all(map(os.path.exists, [CLUSTER_LOG, HEATMAP_FILE])):
        return

    with open(CLUSTER_LOG) as f:
        clusters = json.load(f)
    with open(HEATMAP_FILE) as f:
        heatmap = json.load(f)

    # Aggregate and score
    scores = defaultdict(int)
    for entry in clusters:
        strike = int(entry["strike"])
        scores[strike] += heatmap.get(str(strike), 1)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    with open(OUTPUT, "w") as f:
        f.write("🔝 Top Sniper Cluster Strikes\n\n")
        for strike, score in ranked[:20]:
            f.write(f"{strike}  →  Score: {score}\n")
