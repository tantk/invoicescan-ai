"""Google Sheets integration — dynamic schema for real-world invoices.

Two sheets:
  1. "Invoices" — one row per invoice, columns grow dynamically
     (GST, VAT, service charge, discount — whatever Document AI finds)
  2. "Line Items" — one row per line item, linked by Invoice ID

When a new field type appears (e.g. first invoice with GST), a new column
is added automatically. Existing rows get blank cells — no data is lost.

Auth: Application Default Credentials or service account key file.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import gspread
from google.auth import default
from google.auth.transport.requests import Request

from ..config import SHEETS_SPREADSHEET_ID, SHEETS_ENABLED

logger = logging.getLogger(__name__)

_client: Optional[gspread.Client] = None

# Core columns that always exist in the Invoices sheet
CORE_COLUMNS = [
    "Scan ID",
    "Date Scanned",
    "Filename",
]

# Readable labels for ALL Document AI Invoice Parser field types
FIELD_LABELS = {
    # Identification
    "invoice_id": "Invoice #",
    "invoice_date": "Invoice Date",
    "invoice_type": "Invoice Type",
    "due_date": "Due Date",
    "delivery_date": "Delivery Date",
    "purchase_order": "PO #",
    "payment_terms": "Payment Terms",
    "currency": "Currency",
    "currency_exchange_rate": "Exchange Rate",
    # Supplier
    "supplier_name": "Vendor",
    "supplier_address": "Vendor Address",
    "supplier_phone": "Vendor Phone",
    "supplier_email": "Vendor Email",
    "supplier_website": "Vendor Website",
    "supplier_tax_id": "Vendor Tax ID",
    "supplier_iban": "Vendor IBAN",
    "supplier_registration": "Vendor Reg #",
    "supplier_payment_ref": "Payment Ref",
    # Receiver
    "receiver_name": "Bill To",
    "receiver_address": "Bill To Address",
    "receiver_email": "Customer Email",
    "receiver_phone": "Customer Phone",
    "receiver_tax_id": "Customer Tax ID",
    # Shipping
    "ship_to_name": "Ship To",
    "ship_to_address": "Ship To Address",
    "ship_from_name": "Ship From",
    "ship_from_address": "Ship From Address",
    "carrier": "Carrier",
    "freight_amount": "Shipping",
    # Remittance
    "remit_to_name": "Remit To",
    "remit_to_address": "Remit To Address",
    "currency": "Currency",
    "net_amount": "Subtotal",
    "total_amount": "Total",
    "total_tax_amount": "Tax",
    "vat_tax_amount": "VAT",
    "freight_amount": "Shipping",
    "amount_paid_since_last_invoice": "Paid",
    "remit_to_name": "Remit To",
    "remit_to_address": "Remit To Address",
    # These get added dynamically if Document AI returns them:
    # gst, service_charge, discount, handling_fee, etc.
}


def _field_to_label(field_type: str) -> str:
    """Convert a field type to a readable column header.

    For custom_ prefixed fields (Layer 2), strip the prefix and
    reuse the same label with 'Custom ' prefix:
      custom_supplier_name → Custom Vendor
      custom_project_code  → Custom Project Code
    """
    # Layer 2 custom field
    if field_type.startswith("custom_"):
        base = field_type[7:]  # Remove "custom_"
        base_label = FIELD_LABELS.get(base)
        if base_label:
            return f"Custom {base_label}"
        return f"Custom {base.replace('_', ' ').title()}"

    # Standard Document AI field
    if field_type in FIELD_LABELS:
        return FIELD_LABELS[field_type]

    # Unknown field — auto-generate label
    return field_type.replace("_", " ").title()

# Line Items sheet columns
LINE_ITEM_CORE_COLUMNS = [
    "Scan ID",
    "Item #",
]

LINE_ITEM_FIELD_LABELS = {
    "line_item/description": "Description",
    "line_item/quantity": "Quantity",
    "line_item/unit_price": "Unit Price",
    "line_item/amount": "Amount",
    "line_item/product_code": "Product Code",
    "line_item/unit": "Unit",
    "line_item/tax_amount": "Tax",
    "line_item/tax_rate": "Tax Rate",
    "line_item/discount_amount": "Discount",
    "line_item/discount_rate": "Discount Rate",
}


def _get_client() -> gspread.Client:
    """Get or create an authenticated gspread client."""
    global _client
    if _client is not None:
        return _client

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    key_file = os.environ.get("GOOGLE_SHEETS_KEY_FILE", "")
    if key_file and os.path.exists(key_file):
        _client = gspread.service_account(filename=key_file, scopes=scopes)
    else:
        creds, _ = default(scopes=scopes)
        creds.refresh(Request())
        _client = gspread.authorize(creds)

    return _client


def _get_or_create_worksheet(spreadsheet, title: str, headers: list[str]):
    """Get a worksheet by title, or create it with headers."""
    try:
        ws = spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=1000, cols=len(headers) + 10)
        ws.update("A1", [headers])
        _format_headers(ws, len(headers))
        logger.info(f"Created worksheet '{title}' with {len(headers)} columns")
    return ws


def _format_headers(ws, col_count: int):
    """Bold + colored header row."""
    end_col = chr(ord("A") + min(col_count - 1, 25))  # A-Z
    try:
        ws.format(f"A1:{end_col}1", {
            "textFormat": {"bold": True, "foregroundColor": {"red": 0, "green": 0, "blue": 0}},
            "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.0},
            "horizontalAlignment": "CENTER",
        })
    except Exception:
        pass  # Formatting is nice-to-have, don't fail on it


def _ensure_columns(ws, existing_headers: list[str], needed_headers: list[str]) -> list[str]:
    """Add any new columns that don't exist yet. Returns updated header list."""
    new_cols = [h for h in needed_headers if h not in existing_headers]
    if not new_cols:
        return existing_headers

    updated = existing_headers + new_cols
    # Write the full header row
    ws.update("A1", [updated])
    _format_headers(ws, len(updated))
    logger.info(f"Added {len(new_cols)} new columns: {new_cols}")
    return updated


def _line_item_field_to_label(field_type: str) -> str:
    """Convert a line item field type to a readable column header."""
    if field_type in LINE_ITEM_FIELD_LABELS:
        return LINE_ITEM_FIELD_LABELS[field_type]
    clean = field_type.replace("line_item/", "").replace("_", " ").title()
    return clean


def _extract_value(field_data) -> str:
    """Extract the value string from a field dict or raw value."""
    if isinstance(field_data, dict):
        return field_data.get("value", "")
    return str(field_data)


# ── Main Write Functions ──────────────────────────────────────────────────


def add_invoice_to_sheet(
    invoice_id: str,
    extracted_data: dict,
    filename: Optional[str] = None,
) -> bool:
    """Add a processed invoice to the spreadsheet.

    Dynamically adds columns for any new field types encountered.
    Also writes line items to the "Line Items" sheet.

    Args:
        invoice_id: Unique invoice ID.
        extracted_data: Dict from Document AI (fields, line_items).
        filename: Original filename.

    Returns:
        True if successful.
    """
    if not SHEETS_ENABLED:
        return False

    try:
        client = _get_client()
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)

        # ── Invoices sheet ────────────────────────────────────────────
        fields = extracted_data.get("fields", {})

        # Build labels for all fields in this invoice
        field_labels = {_field_to_label(k): _extract_value(v) for k, v in fields.items()}

        # All columns we need (core + all field labels)
        needed_headers = CORE_COLUMNS + list(field_labels.keys())

        # Get or create the Invoices sheet
        invoices_ws = _get_or_create_worksheet(spreadsheet, "Invoices", needed_headers)

        # Get current headers and expand if needed
        current_headers = invoices_ws.row_values(1)
        if not current_headers:
            current_headers = needed_headers
            invoices_ws.update("A1", [current_headers])
            _format_headers(invoices_ws, len(current_headers))
        else:
            current_headers = _ensure_columns(invoices_ws, current_headers, needed_headers)

        # Build the row (aligned to current headers)
        row = []
        for header in current_headers:
            if header == "Scan ID":
                row.append(invoice_id)
            elif header == "Date Scanned":
                row.append(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
            elif header == "Filename":
                row.append(filename or "")
            elif header in field_labels:
                row.append(field_labels[header])
            else:
                row.append("")  # Column exists from another invoice, blank for this one

        invoices_ws.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"Added invoice {invoice_id} to Invoices sheet ({len(field_labels)} fields)")

        # ── Line Items sheet ──────────────────────────────────────────
        line_items = extracted_data.get("line_items", [])
        if line_items:
            _write_line_items(spreadsheet, invoice_id, line_items)

        # ── VAT Breakdown sheet ──────────────────────────────────────
        vat_breakdown = extracted_data.get("vat_breakdown", [])
        if vat_breakdown:
            _write_vat_breakdown(spreadsheet, invoice_id, vat_breakdown)

        return True

    except Exception as e:
        logger.error(f"Failed to add invoice to sheet: {e}")
        return False


def _write_line_items(spreadsheet, invoice_id: str, line_items: list[dict]):
    """Write line items to the Line Items sheet."""
    # Collect all field types across all line items
    all_field_types = set()
    for item in line_items:
        all_field_types.update(item.keys())

    item_labels = {k: _line_item_field_to_label(k) for k in all_field_types}
    needed_headers = LINE_ITEM_CORE_COLUMNS + [item_labels[k] for k in sorted(all_field_types)]

    items_ws = _get_or_create_worksheet(spreadsheet, "Line Items", needed_headers)

    current_headers = items_ws.row_values(1)
    if not current_headers:
        current_headers = needed_headers
        items_ws.update("A1", [current_headers])
        _format_headers(items_ws, len(current_headers))
    else:
        current_headers = _ensure_columns(items_ws, current_headers, needed_headers)

    # Build rows for all line items
    rows = []
    for i, item in enumerate(line_items, 1):
        row = []
        for header in current_headers:
            if header == "Scan ID":
                row.append(invoice_id)
            elif header == "Item #":
                row.append(str(i))
            else:
                # Find the field type that maps to this header
                value = ""
                for field_type, label in item_labels.items():
                    if label == header and field_type in item:
                        value = _extract_value(item[field_type])
                        break
                row.append(value)
        rows.append(row)

    if rows:
        items_ws.append_rows(rows, value_input_option="USER_ENTERED")
        logger.info(f"Added {len(rows)} line items for invoice {invoice_id}")


def _write_vat_breakdown(spreadsheet, invoice_id: str, vat_breakdown: list[dict]):
    """Write VAT breakdown to the Tax Breakdown sheet."""
    VAT_LABELS = {
        "vat/amount": "Taxable Amount",
        "vat/tax_amount": "Tax Amount",
        "vat/tax_rate": "Rate",
        "vat/category_code": "Category",
        "amount": "Taxable Amount",
        "tax_amount": "Tax Amount",
        "tax_rate": "Rate",
        "category_code": "Category",
    }

    all_keys = set()
    for entry in vat_breakdown:
        all_keys.update(entry.keys())

    vat_labels = {k: VAT_LABELS.get(k, k.replace("_", " ").title()) for k in all_keys}
    needed_headers = ["Scan ID"] + [vat_labels[k] for k in sorted(all_keys)]

    vat_ws = _get_or_create_worksheet(spreadsheet, "Tax Breakdown", needed_headers)

    current_headers = vat_ws.row_values(1)
    if not current_headers:
        current_headers = needed_headers
        vat_ws.update("A1", [current_headers])
        _format_headers(vat_ws, len(current_headers))
    else:
        current_headers = _ensure_columns(vat_ws, current_headers, needed_headers)

    rows = []
    for entry in vat_breakdown:
        row = []
        for header in current_headers:
            if header == "Scan ID":
                row.append(invoice_id)
            else:
                value = ""
                for field_type, label in vat_labels.items():
                    if label == header and field_type in entry:
                        value = _extract_value(entry[field_type])
                        break
                row.append(value)
        rows.append(row)

    if rows:
        vat_ws.append_rows(rows, value_input_option="USER_ENTERED")
        logger.info(f"Added {len(rows)} VAT breakdown entries for invoice {invoice_id}")


# ── Agent Tools ───────────────────────────────────────────────────────────


def add_to_spreadsheet(invoice_id: str) -> dict:
    """Add an invoice's extracted data to the Google Sheet.

    Use this when the user asks to save or log an invoice to their spreadsheet.
    The invoice data goes to the "Invoices" sheet, line items to "Line Items".

    Args:
        invoice_id: The ID of the invoice to add.

    Returns:
        Status message confirming the row was added.
    """
    from .invoice_parser import invoice_store

    if not SHEETS_ENABLED:
        return {"error": "Google Sheets is not configured. Set SHEETS_SPREADSHEET_ID in .env."}

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    if "extracted_data" not in invoice:
        return {"error": "No extracted data. Process the invoice with parse_invoice first."}

    success = add_invoice_to_sheet(
        invoice_id=invoice_id,
        extracted_data=invoice["extracted_data"],
        filename=invoice.get("filename"),
    )

    if success:
        line_count = len(invoice["extracted_data"].get("line_items", []))
        return {
            "status": "success",
            "message": (
                f"Invoice {invoice_id} added to spreadsheet. "
                f"{'Line items (' + str(line_count) + ') added to Line Items sheet.' if line_count else ''}"
            ),
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{SHEETS_SPREADSHEET_ID}",
        }
    return {"status": "error", "message": "Failed to add to spreadsheet."}


def add_remark(invoice_id: str, remark: str) -> dict:
    """Add a remark/note to an invoice in the Google Sheet.

    Use this when the user makes a comment about an invoice during conversation.
    Examples: "this is for the office renovation", "follow up with vendor",
    "approved by John", "need receipt for this one", "quarterly subscription".

    The remark is appended to the Remarks column for that invoice's row.
    If the invoice already has a remark, the new one is appended with a semicolon.

    Args:
        invoice_id: The invoice to add a remark to.
        remark: The user's note/comment about the invoice.

    Returns:
        Confirmation that the remark was saved.
    """
    if not SHEETS_ENABLED:
        return {"error": "Google Sheets is not configured."}

    try:
        client = _get_client()
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)
        invoices_ws = spreadsheet.worksheet("Invoices")

        all_values = invoices_ws.get_all_values()
        if not all_values:
            return {"error": "Sheet is empty."}

        headers = all_values[0]

        # Ensure Remarks column exists
        if "Remarks" not in headers:
            col_index = len(headers) + 1
            invoices_ws.update_cell(1, col_index, "Remarks")
            headers.append("Remarks")
            _format_headers(invoices_ws, len(headers))

        remarks_col = headers.index("Remarks") + 1  # 1-based
        scan_id_col = headers.index("Scan ID") + 1 if "Scan ID" in headers else 1

        # Find the row with this invoice_id
        target_row = None
        for row_idx, row in enumerate(all_values[1:], start=2):  # 2-based (skip header)
            cell_value = row[scan_id_col - 1] if len(row) >= scan_id_col else ""
            if cell_value == invoice_id:
                target_row = row_idx
                break

        if target_row is None:
            return {"error": f"Invoice {invoice_id} not found in the sheet."}

        # Get existing remark (if any) and append
        existing = invoices_ws.cell(target_row, remarks_col).value or ""
        if existing:
            new_remark = f"{existing}; {remark}"
        else:
            new_remark = remark

        invoices_ws.update_cell(target_row, remarks_col, new_remark)

        logger.info(f"Remark added for invoice {invoice_id}: {remark}")

        return {
            "status": "success",
            "invoice_id": invoice_id,
            "remark": new_remark,
            "message": f"Remark saved for invoice {invoice_id}.",
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{SHEETS_SPREADSHEET_ID}",
        }

    except Exception as e:
        logger.error(f"Failed to add remark: {e}")
        return {"error": f"Failed to save remark: {str(e)}"}


def update_analysis_column(invoice_id: str, analysis_text: str) -> dict:
    """Write post-processing analysis results to the Analysis column in Google Sheets.

    Called by the server after background analysis (fraud, confidence, compliance)
    completes. Writes a summary to the Analysis column for that invoice's row.

    Args:
        invoice_id: The invoice to update.
        analysis_text: The analysis summary text.

    Returns:
        Confirmation that the analysis was saved.
    """
    if not SHEETS_ENABLED:
        return {"error": "Google Sheets is not configured."}

    try:
        client = _get_client()
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)
        invoices_ws = spreadsheet.worksheet("Invoices")

        all_values = invoices_ws.get_all_values()
        if not all_values:
            return {"error": "Sheet is empty."}

        headers = all_values[0]

        # Ensure Analysis column exists
        if "Analysis" not in headers:
            col_index = len(headers) + 1
            invoices_ws.update_cell(1, col_index, "Analysis")
            headers.append("Analysis")
            _format_headers(invoices_ws, len(headers))

        analysis_col = headers.index("Analysis") + 1  # 1-based
        scan_id_col = headers.index("Scan ID") + 1 if "Scan ID" in headers else 1

        # Find the row with this invoice_id
        target_row = None
        for row_idx, row in enumerate(all_values[1:], start=2):
            cell_value = row[scan_id_col - 1] if len(row) >= scan_id_col else ""
            if cell_value == invoice_id:
                target_row = row_idx
                break

        if target_row is None:
            return {"error": f"Invoice {invoice_id} not found in the sheet."}

        invoices_ws.update_cell(target_row, analysis_col, analysis_text)

        logger.info(f"Analysis written for invoice {invoice_id}")

        return {
            "status": "success",
            "invoice_id": invoice_id,
            "message": f"Analysis saved for invoice {invoice_id}.",
        }

    except Exception as e:
        logger.error(f"Failed to write analysis: {e}")
        return {"error": f"Failed to save analysis: {str(e)}"}


def get_spreadsheet_summary() -> dict:
    """Get a summary of the invoice spreadsheet — total rows, recent entries, columns.

    Use this when the user asks about their spreadsheet or invoice log.

    Returns:
        Summary with row count, column list, and recent entries.
    """
    if not SHEETS_ENABLED:
        return {"error": "Google Sheets is not configured."}

    try:
        client = _get_client()
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)

        result = {
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{SHEETS_SPREADSHEET_ID}",
            "sheets": {},
        }

        # Invoices sheet
        try:
            invoices_ws = spreadsheet.worksheet("Invoices")
            all_values = invoices_ws.get_all_values()
            headers = all_values[0] if all_values else []
            data_rows = all_values[1:] if len(all_values) > 1 else []

            recent = []
            for row in data_rows[-5:]:
                entry = {}
                for i, header in enumerate(headers):
                    if i < len(row) and row[i]:
                        entry[header] = row[i]
                recent.append(entry)

            result["sheets"]["Invoices"] = {
                "total_rows": len(data_rows),
                "columns": headers,
                "recent": recent,
            }
        except gspread.WorksheetNotFound:
            result["sheets"]["Invoices"] = {"total_rows": 0, "message": "No invoices yet."}

        # Line Items sheet
        try:
            items_ws = spreadsheet.worksheet("Line Items")
            item_count = max(0, len(items_ws.get_all_values()) - 1)
            result["sheets"]["Line Items"] = {"total_rows": item_count}
        except gspread.WorksheetNotFound:
            result["sheets"]["Line Items"] = {"total_rows": 0}

        return result

    except Exception as e:
        return {"error": f"Failed to read spreadsheet: {str(e)}"}
