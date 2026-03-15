"""Invoice fraud detection and duplicate checking.

Checks every invoice for:
1. Exact duplicates (same invoice # + vendor)
2. Near duplicates (same amount + vendor within 30 days)
3. Suspicious patterns (same amount from different vendors)
4. Round number flags
5. Bank detail changes
6. Weekend-dated invoices
7. Sequential anomalies
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def _parse_amount(val) -> Optional[float]:
    """Parse a currency amount from various formats."""
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("value", "")
    val = str(val)
    cleaned = re.sub(r"[^\d.\-]", "", val.replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(val) -> Optional[datetime]:
    """Parse a date from various formats."""
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("value", "")
    val = str(val).strip()
    if not val:
        return None

    for fmt in (
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
        "%d %b %Y", "%B %d, %Y", "%b %d, %Y",
        "%d.%m.%Y", "%Y年%m月%d日",
    ):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None


def _normalize_vendor(name: str) -> str:
    """Normalize vendor name for comparison."""
    if not name:
        return ""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def check_duplicate(invoice_id: str) -> dict:
    """Check an invoice for duplicates and fraud indicators.

    Compares against all previously scanned invoices. Flags:
    - Exact duplicates (same invoice number + vendor)
    - Near duplicates (same amount + vendor within 30 days)
    - Suspicious patterns (same amount, different vendors)
    - Round number amounts
    - Weekend-dated invoices
    - Sequential invoice number gaps

    Call this on every new invoice to catch issues early.

    Args:
        invoice_id: The ID of the invoice to check.

    Returns:
        Fraud check results with flags, warnings, and risk level.
    """
    from .invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    extracted = invoice.get("extracted_data", {})
    fields = extracted.get("fields", {})

    # Current invoice details
    cur_inv_num = fields.get("invoice_id", {})
    cur_inv_num = cur_inv_num.get("value", "") if isinstance(cur_inv_num, dict) else str(cur_inv_num or "")

    cur_vendor = fields.get("supplier_name", {})
    cur_vendor = cur_vendor.get("value", "") if isinstance(cur_vendor, dict) else str(cur_vendor or "")

    cur_amount = _parse_amount(fields.get("total_amount"))
    cur_date = _parse_date(fields.get("invoice_date"))

    cur_iban = fields.get("supplier_iban", {})
    cur_iban = cur_iban.get("value", "") if isinstance(cur_iban, dict) else str(cur_iban or "")

    result = {
        "invoice_id": invoice_id,
        "flags": [],
        "risk_level": "LOW",
    }

    # ── Check 1: Round number ─────────────────────────────────────────
    if cur_amount is not None:
        if cur_amount > 0 and cur_amount == int(cur_amount) and cur_amount >= 100:
            result["flags"].append({
                "type": "ROUND_NUMBER",
                "severity": "LOW",
                "detail": f"Exact round amount: {cur_amount:.2f}. Round numbers are statistically unusual in real invoices.",
            })

        # Very round (ends in 000 or 500)
        if cur_amount >= 1000 and (cur_amount % 1000 == 0 or cur_amount % 500 == 0):
            result["flags"][-1]["severity"] = "MEDIUM" if result["flags"] else None
            if not result["flags"] or result["flags"][-1]["type"] != "ROUND_NUMBER":
                result["flags"].append({
                    "type": "ROUND_NUMBER",
                    "severity": "MEDIUM",
                    "detail": f"Very round amount: {cur_amount:.2f}. Amounts ending in 000/500 are common in fraudulent invoices.",
                })

    # ── Check 2: Weekend date ─────────────────────────────────────────
    if cur_date is not None:
        if cur_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            day_name = "Saturday" if cur_date.weekday() == 5 else "Sunday"
            result["flags"].append({
                "type": "WEEKEND_DATE",
                "severity": "LOW",
                "detail": f"Invoice dated on {day_name} ({cur_date.strftime('%Y-%m-%d')}). Most businesses don't issue invoices on weekends.",
            })

    # ── Compare against all other invoices ────────────────────────────
    # Layer 1: Current session (in-memory) — catches accidental double-scans
    # Layer 2: Vertex AI Search (history) — catches cross-session duplicates
    exact_dupes = []
    near_dupes = []
    amount_matches = []
    bank_changes = []
    vendor_inv_numbers = []

    cur_vendor_norm = _normalize_vendor(cur_vendor)

    # ── Layer 1: In-memory (current session — most important) ─────────
    candidates = {}
    for other_id, other_inv in invoice_store.items():
        if other_id == invoice_id:
            continue
        other_extracted = other_inv.get("extracted_data", {})
        if other_extracted:
            candidates[other_id] = {"fields": other_extracted.get("fields", {}), "source": "session"}

    # ── Layer 2: Vertex AI Search (historical — cross-session) ────────
    try:
        from .search_store import search_invoices
        if cur_vendor:
            search_results = search_invoices(
                query=f"{cur_vendor} {cur_inv_num} {cur_amount or ''}",
                max_results=10,
            )
            for sr in search_results:
                sr_id = sr.get("id", "")
                if sr_id and sr_id != invoice_id and sr_id not in candidates:
                    # Convert search result data to field format
                    sr_data = sr.get("data", {})
                    if sr_data:
                        sr_fields = {k: {"value": v, "confidence": 1.0} for k, v in sr_data.items() if v}
                        candidates[sr_id] = {"fields": sr_fields, "source": "history"}
    except Exception as e:
        logger.debug(f"Vertex AI Search check skipped: {e}")

    # ── Run checks against all candidates ─────────────────────────────
    for other_id, candidate in candidates.items():
        other_fields = candidate["fields"]
        match_source = candidate["source"]

        other_inv_num = other_fields.get("invoice_id", {})
        other_inv_num = other_inv_num.get("value", "") if isinstance(other_inv_num, dict) else str(other_inv_num or "")

        other_vendor = other_fields.get("supplier_name", {})
        other_vendor = other_vendor.get("value", "") if isinstance(other_vendor, dict) else str(other_vendor or "")

        other_amount = _parse_amount(other_fields.get("total_amount"))
        other_date = _parse_date(other_fields.get("invoice_date"))

        other_iban = other_fields.get("supplier_iban", {})
        other_iban = other_iban.get("value", "") if isinstance(other_iban, dict) else str(other_iban or "")

        other_vendor_norm = _normalize_vendor(other_vendor)
        same_vendor = cur_vendor_norm and other_vendor_norm and cur_vendor_norm == other_vendor_norm

        # Check 3: Exact duplicate (same invoice # + same vendor)
        if cur_inv_num and other_inv_num and cur_inv_num == other_inv_num and same_vendor:
            exact_dupes.append({
                "other_invoice_id": other_id,
                "invoice_number": cur_inv_num,
                "vendor": cur_vendor,
                "source": match_source,
            })

        # Check 4: Near duplicate (same vendor + same amount within 30 days)
        if same_vendor and cur_amount is not None and other_amount is not None:
            if abs(cur_amount - other_amount) < 0.02:
                days_apart = None
                if cur_date and other_date:
                    days_apart = abs((cur_date - other_date).days)

                if days_apart is None or days_apart <= 30:
                    near_dupes.append({
                        "other_invoice_id": other_id,
                        "vendor": cur_vendor,
                        "amount": cur_amount,
                        "days_apart": days_apart,
                    })

        # Check 5: Same amount from different vendor within 7 days
        if not same_vendor and cur_amount is not None and other_amount is not None:
            if abs(cur_amount - other_amount) < 0.02 and cur_amount >= 100:
                days_apart = None
                if cur_date and other_date:
                    days_apart = abs((cur_date - other_date).days)

                if days_apart is not None and days_apart <= 7:
                    amount_matches.append({
                        "other_invoice_id": other_id,
                        "this_vendor": cur_vendor,
                        "other_vendor": other_vendor,
                        "amount": cur_amount,
                        "days_apart": days_apart,
                    })

        # Check 6: Bank detail change for same vendor
        if same_vendor and cur_iban and other_iban and cur_iban != other_iban:
            bank_changes.append({
                "other_invoice_id": other_id,
                "vendor": cur_vendor,
                "previous_iban": other_iban,
                "current_iban": cur_iban,
            })

        # Collect invoice numbers from same vendor for sequence check
        if same_vendor and other_inv_num:
            vendor_inv_numbers.append(other_inv_num)

    # ── Build flags ───────────────────────────────────────────────────

    if exact_dupes:
        for ed in exact_dupes:
            source_text = "earlier in this session" if ed["source"] == "session" else "in invoice history"
            result["flags"].append({
                "type": "EXACT_DUPLICATE",
                "severity": "CRITICAL",
                "detail": f"Exact duplicate! Invoice #{cur_inv_num} from {cur_vendor} was already scanned {source_text}.",
                "match": ed,
            })

    if near_dupes:
        for nd in near_dupes:
            days_text = f" ({nd['days_apart']} days apart)" if nd['days_apart'] is not None else ""
            result["flags"].append({
                "type": "NEAR_DUPLICATE",
                "severity": "HIGH",
                "detail": (
                    f"Very similar invoice: same vendor ({nd['vendor']}) and same amount "
                    f"(${nd['amount']:.2f}){days_text}. Could be a re-submitted invoice."
                ),
                "match": nd,
            })

    if amount_matches:
        for am in amount_matches:
            result["flags"].append({
                "type": "SUSPICIOUS_AMOUNT",
                "severity": "MEDIUM",
                "detail": (
                    f"Same amount (${am['amount']:.2f}) from different vendors "
                    f"({am['this_vendor']} vs {am['other_vendor']}) "
                    f"within {am['days_apart']} days. Could indicate split billing."
                ),
                "match": am,
            })

    if bank_changes:
        for bc in bank_changes:
            result["flags"].append({
                "type": "BANK_CHANGE",
                "severity": "HIGH",
                "detail": (
                    f"Bank details changed for {bc['vendor']}! "
                    f"Previous IBAN: {bc['previous_iban']}, Current: {bc['current_iban']}. "
                    f"Verify this change with the vendor — could indicate account takeover."
                ),
                "match": bc,
            })

    # ── Check 7: Invoice number sequence gap ──────────────────────────
    if cur_inv_num and vendor_inv_numbers:
        # Try to extract numeric part and check sequence
        cur_nums = re.findall(r"\d+", cur_inv_num)
        if cur_nums:
            cur_num = int(cur_nums[-1])
            prev_nums = []
            for vn in vendor_inv_numbers:
                nums = re.findall(r"\d+", vn)
                if nums:
                    prev_nums.append(int(nums[-1]))

            if prev_nums:
                max_prev = max(prev_nums)
                if cur_num > max_prev + 1:
                    gap = cur_num - max_prev - 1
                    result["flags"].append({
                        "type": "SEQUENCE_GAP",
                        "severity": "LOW",
                        "detail": (
                            f"Invoice number gap: got #{cur_num} but last was #{max_prev} "
                            f"({gap} missing invoice{'s' if gap > 1 else ''}). "
                            f"May indicate missing invoices from {cur_vendor}."
                        ),
                    })

    # ── Determine overall risk level ──────────────────────────────────
    severities = [f["severity"] for f in result["flags"]]
    if "CRITICAL" in severities:
        result["risk_level"] = "CRITICAL"
    elif "HIGH" in severities:
        result["risk_level"] = "HIGH"
    elif "MEDIUM" in severities:
        result["risk_level"] = "MEDIUM"
    elif severities:
        result["risk_level"] = "LOW"
    else:
        result["risk_level"] = "CLEAN"
        result["flags"].append({
            "type": "ALL_CLEAR",
            "severity": "NONE",
            "detail": "No duplicate or fraud indicators found. Invoice appears clean.",
        })

    result["total_flags"] = len([f for f in result["flags"] if f["severity"] != "NONE"])

    return result
