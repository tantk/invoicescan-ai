"""Currency detection and conversion.

Uses free exchange rate APIs to convert invoice amounts to the user's
preferred display currency. Rates are cached for 1 hour.
"""

import json as _json
import logging
import os
import re
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# In-memory cache (fast)
_rate_cache: dict = {}
CACHE_TTL = 86400  # 24 hours

# Local JSON file — just a rate cache, not worth a database
RATE_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "rate_cache.json")

# Currency symbol → ISO code mapping
SYMBOL_TO_CODE = {
    "$": "USD", "US$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",  # Also CNY — context-dependent
    "₹": "INR", "Rs": "INR", "Rs.": "INR",
    "A$": "AUD",
    "C$": "CAD",
    "S$": "SGD",
    "HK$": "HKD",
    "NZ$": "NZD",
    "R$": "BRL",
    "RM": "MYR",
    "₩": "KRW",
    "฿": "THB",
    "₺": "TRY",
    "₱": "PHP",
    "₫": "VND",
    "₦": "NGN",
    "₪": "ILS",
    "Rp": "IDR",
    "R": "ZAR",
    "zł": "PLN",
    "Kč": "CZK",
    "Ft": "HUF",
    "CHF": "CHF",
    "kr": "SEK",  # Also NOK, DKK — context-dependent
    "₡": "CRC",
    "৳": "BDT",
}


def detect_currency(fields: dict) -> str:
    """Detect the currency code from Document AI extracted fields."""
    currency_field = fields.get("currency", {})
    raw = currency_field.get("value", "") if isinstance(currency_field, dict) else str(currency_field or "")
    raw = raw.strip()

    if not raw:
        return "USD"  # Default

    # Already an ISO code?
    if len(raw) == 3 and raw.isalpha():
        return raw.upper()

    # Symbol lookup
    if raw in SYMBOL_TO_CODE:
        return SYMBOL_TO_CODE[raw]

    # Try to find a symbol in the total amount
    total = fields.get("total_amount", {})
    total_val = total.get("value", "") if isinstance(total, dict) else str(total or "")
    for symbol, code in SYMBOL_TO_CODE.items():
        if symbol in total_val:
            return code

    return "USD"


def _load_stored_rates(base: str) -> Optional[dict]:
    """Load cached rates from local JSON file."""
    try:
        if os.path.exists(RATE_STORE_PATH):
            with open(RATE_STORE_PATH, "r") as f:
                store = _json.load(f)
                return store.get(base)
    except Exception:
        pass
    return None


def _save_stored_rates(base: str, entry: dict):
    """Save rates to local JSON file."""
    try:
        store = {}
        if os.path.exists(RATE_STORE_PATH):
            with open(RATE_STORE_PATH, "r") as f:
                store = _json.load(f)
        store[base] = entry
        with open(RATE_STORE_PATH, "w") as f:
            _json.dump(store, f)
    except Exception:
        pass


def _fetch_rates(base: str) -> Optional[dict]:
    """Fetch exchange rates. Priority: memory cache → disk store → API.

    Rates are stored to disk and only refreshed from API when older than 24h.
    """
    now = time.time()
    base = base.upper()

    # 1. Memory cache (instant)
    if base in _rate_cache:
        cached = _rate_cache[base]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["rates"]

    # 2. Firestore (survives restarts, shared across instances)
    stored_entry = _load_stored_rates(base)
    if stored_entry:
        age = now - stored_entry.get("timestamp", 0)
        if age < CACHE_TTL:
            _rate_cache[base] = stored_entry
            logger.info(f"Loaded rates for {base} from Firestore ({age/3600:.1f}h old)")
            return stored_entry["rates"]
        else:
            logger.info(f"Firestore rates for {base} are {age/3600:.1f}h old — refreshing")

    # 3. API (refresh when stale or missing)
    try:
        resp = httpx.get(
            f"https://api.exchangerate-api.com/v4/latest/{base}",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            rates = data.get("rates", {})
            entry = {"rates": rates, "timestamp": now}

            # Save to memory + Firestore
            _rate_cache[base] = entry
            _save_stored_rates(base, entry)

            logger.info(f"Fetched fresh rates for {base} from API ({len(rates)} currencies)")
            return rates
    except Exception as e:
        logger.debug(f"Exchange rate API unavailable: {e}")

    # 4. Use stale Firestore rates if API failed (better than nothing)
    if stored_entry:
        _rate_cache[base] = stored_entry
        age = (now - stored_entry.get("timestamp", 0)) / 3600
        logger.warning(f"Using stale rates for {base} ({age:.0f}h old — API unavailable)")
        return stored_entry["rates"]

    return None


def convert_amount(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> Optional[dict]:
    """Convert an amount between currencies.

    Args:
        amount: The amount to convert.
        from_currency: Source ISO currency code.
        to_currency: Target ISO currency code.

    Returns:
        Conversion result with rate and converted amount.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return {
            "original_amount": amount,
            "converted_amount": amount,
            "from": from_currency,
            "to": to_currency,
            "rate": 1.0,
        }

    rates = _fetch_rates(from_currency)
    if not rates or to_currency not in rates:
        return None

    rate = rates[to_currency]
    converted = round(amount * rate, 2)

    return {
        "original_amount": amount,
        "converted_amount": converted,
        "from": from_currency,
        "to": to_currency,
        "rate": round(rate, 6),
    }


def parse_and_convert(
    amount_str: str,
    from_currency: str,
    to_currency: str,
) -> Optional[dict]:
    """Parse an amount string and convert to target currency."""
    # Strip currency symbols and parse
    cleaned = re.sub(r"[^\d.\-,]", "", str(amount_str))
    # Handle comma as thousands separator or decimal
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")  # 1,234.56 format
    elif "," in cleaned:
        # Could be 1.234,56 (EU) or 1,234 (US with no decimals)
        parts = cleaned.split(",")
        if len(parts[-1]) == 2:
            cleaned = cleaned.replace(".", "").replace(",", ".")  # EU format
        else:
            cleaned = cleaned.replace(",", "")  # US thousands

    try:
        amount = float(cleaned)
    except ValueError:
        return None

    return convert_amount(amount, from_currency, to_currency)
