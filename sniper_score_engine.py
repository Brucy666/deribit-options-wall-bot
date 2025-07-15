from strike_cluster import extract_strike
from cluster_memory import is_repeated_cluster
from heatmap_builder import load_heatmap

# Scoring weights
CLUSTER_HIT_WEIGHT = 1
CLUSTER_REPEAT_BONUS = 3
HEATMAP_MULTIPLIER = 0.5

# Score a single option wall
def score_strike(data):
    strike = extract_strike(data["symbol"])
    if strike is None:
        return 0

    score = 0
    if is_repeated_cluster(strike):
        score += CLUSTER_REPEAT_BONUS

    heatmap = load_heatmap()
    if str(strike) in heatmap:
        score += heatmap[str(strike)] * HEATMAP_MULTIPLIER

    return round(score, 2)
