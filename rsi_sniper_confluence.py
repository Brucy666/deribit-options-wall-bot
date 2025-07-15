from strike_cluster import extract_strike
from sniper_score_engine import score_strike

# 🧪 Force RSI divergence to always trigger
def rsi_divergence_detected(symbol):
    return True  # 🔁 TEMPORARY test override

# Combined sniper confluence logic
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
    return score >= 5
