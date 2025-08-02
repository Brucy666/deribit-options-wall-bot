def detect_trap_wall(wall, wall_memory, current_price, rsi_fast=None, rsi_slow=None):
    """
    Identify potential trap setups:
    - Wall has been seen before
    - Price is near the strike
    - RSI fast/slow suggest stall
    """

    key = f"{wall['strike']}-{wall['type']}-{wall['expiry']}"
    memory = wall_memory.get(key, {})
    seen_count = memory.get("seen_count", 0)

    dist_pct = abs(current_price - wall["strike"]) / current_price * 100
    is_close = dist_pct < 1.0

    # RSI trap: fast > 65 but flattening or slow > 60
    rsi_condition = False
    if rsi_fast is not None and rsi_slow is not None:
        rsi_condition = (
            rsi_fast > 65 and rsi_fast < rsi_slow + 2  # no momentum follow-through
        )

    if seen_count >= 2 and is_close:
        if rsi_condition:
            return {
                "is_trap": True,
                "reason": f"🔴 Trap Detected → Wall seen {seen_count}x near price, RSI failing",
                "strike": wall["strike"],
                "type": wall["type"],
                "seen": seen_count,
                "dist_pct": round(dist_pct, 2)
            }

    return {"is_trap": False}
