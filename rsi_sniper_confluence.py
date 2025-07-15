from strike_cluster import extract_strike
from sniper_score_engine import score_strike

# Simulated RSI divergence signal check
def rsi_divergence_detected(symbol):
    # This would be your actual RSI logic — simplified here
    return "PUT" in symbol or "CALL" in symbol  # just for test

# Combined sniper logic
def is_high_confluence_sniper(symbol):
    if not rsi_divergence_detected(symbol):
        return False

    fake_data = {
        "symbol": symbol,
        "open_interest": 1200,
        "volume": 25,
        "last": 0
    }

    score = score_strike(fake_data)
    print(f"Scoring {symbol} → {score}")
    return score >= 5
