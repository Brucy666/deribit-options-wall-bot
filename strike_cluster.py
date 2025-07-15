import re

# Grouping window (±100 for strike rounding)
STRIKE_WINDOW = 100

# Extract numeric strike from symbol
def extract_strike(symbol):
    try:
        match = re.search(r"BTC-\d{2}[A-Z]{3}\d{2}-(\d+)-[CP]", symbol)
        return int(match.group(1)) if match else None
    except:
        return None

# Group similar strike zones
def detect_clusters(data_list):
    # Collect all strikes
    strikes = []
    for item in data_list:
        strike = extract_strike(item["symbol"])
        if strike:
            strikes.append(strike)

    # Count nearby clusters
    clusters = {}
    for strike in strikes:
        for other in strikes:
            if abs(strike - other) <= STRIKE_WINDOW:
                clusters.setdefault(strike, []).append(other)

    # Find clusters with more than 2 walls
    valid_clusters = {k: v for k, v in clusters.items() if len(v) >= 3}
    return list(valid_clusters.keys())

# Mark if this symbol is part of a cluster
def is_cluster_strike(symbol, cluster_list):
    strike = extract_strike(symbol)
    return any(abs(strike - c) <= STRIKE_WINDOW for c in cluster_list)
