import statistics

def score_wall_bias(current_price, wall_memory):
    """
    Analyzes wall memory and returns a bias score and signal.
    """

    call_walls = []
    put_walls = []

    for key, wall in wall_memory.items():
        distance_pct = abs(current_price - wall["strike"]) / current_price
        if distance_pct > 0.03:  # Only consider walls within 3%
            continue

        record = {
            "strike": wall["strike"],
            "seen_count": wall.get("seen_count", 1),
            "oi": wall["oi"],
            "volume": wall["volume"],
            "distance": distance_pct
        }

        if wall["type"] == "C":
            call_walls.append(record)
        elif wall["type"] == "P":
            put_walls.append(record)

    call_strength = sum(w["oi"] * w["seen_count"] for w in call_walls)
    put_strength = sum(w["oi"] * w["seen_count"] for w in put_walls)

    trap_risk = len(call_walls + put_walls) >= 5 and any(w["distance"] < 0.01 for w in call_walls + put_walls)

    score = 0
    bias = "neutral"

    if call_strength > put_strength * 1.2:
        score = -1
        bias = "bearish"
    elif put_strength > call_strength * 1.2:
        score = +1
        bias = "bullish"

    if trap_risk:
        bias = "trap_zone"
        score = -2 if score <= 0 else score

    return {
        "bias": bias,
        "score": score,
        "call_strength": call_strength,
        "put_strength": put_strength,
        "wall_count": len(call_walls + put_walls),
        "active_call_walls": call_walls,
        "active_put_walls": put_walls
    }
