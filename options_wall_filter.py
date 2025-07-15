from datetime import datetime, timedelta
import re

# Adjustable filters
MIN_OI = 500
MIN_VOL = 10
EXCLUDE_DAYS = 3

# Helper to parse expiry from Deribit symbol (e.g. BTC-26JUL24-60000-C)
def parse_expiry(symbol):
    try:
        match = re.search(r"BTC-(\d{2}[A-Z]{3}\d{2})-", symbol)
        if not match:
            return None
        date_str = match.group(1)
        return datetime.strptime(date_str, "%d%b%y")
    except Exception:
        return None

# Filter logic
def is_valid_wall(data):
    expiry = parse_expiry(data["symbol"])
    if not expiry:
        return False
    days_to_expiry = (expiry - datetime.utcnow()).days
    if days_to_expiry < EXCLUDE_DAYS:
        return False
    if data["open_interest"] < MIN_OI:
        return False
    if data["volume"] < MIN_VOL:
        return False
    return True
