"""Invoice parsing with Google Document AI for grounded extraction.

Document AI provides the structured grounding layer — the agent uses this
verified data instead of guessing from vision alone.
"""

import json
import logging
from typing import Optional

from ..config import DOCAI_ENABLED, DOCAI_LOCATION, DOCAI_PROCESSOR_ID, GCP_PROJECT

logger = logging.getLogger(__name__)

# In-memory invoice store: invoice_id -> {image_bytes, mime_type, extracted_data, grounding_text}
invoice_store: dict = {}


# ── Document AI Processing ────────────────────────────────────────────────


def _call_document_ai(image_bytes: bytes, mime_type: str) -> dict:
    """Call Document AI Invoice Parser and return structured extraction."""
    from google.cloud import documentai

    client = documentai.DocumentProcessorServiceClient(
        client_options={
            "api_endpoint": f"{DOCAI_LOCATION}-documentai.googleapis.com"
        }
    )

    processor_name = (
        f"projects/{GCP_PROJECT}/locations/{DOCAI_LOCATION}"
        f"/processors/{DOCAI_PROCESSOR_ID}"
    )

    response = client.process_document(
        request=documentai.ProcessRequest(
            name=processor_name,
            raw_document=documentai.RawDocument(
                content=image_bytes, mime_type=mime_type
            ),
        )
    )

    document = response.document
    return _extract_structured_data(document)


def _get_bounding_box(entity) -> Optional[list]:
    """Extract normalized bounding box from a Document AI entity.

    Returns [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] normalized (0-1).
    """
    try:
        if entity.page_anchor and entity.page_anchor.page_refs:
            for page_ref in entity.page_anchor.page_refs:
                if hasattr(page_ref, 'bounding_poly') and page_ref.bounding_poly:
                    verts = page_ref.bounding_poly.normalized_vertices
                    if verts:
                        return [[round(v.x, 4), round(v.y, 4)] for v in verts]
    except Exception:
        pass
    return None


def _extract_structured_data(document) -> dict:
    """Convert Document AI response into a clean structured dict.

    Handles all Invoice Parser entity types with bounding boxes for overlay.
    """
    result = {
        "full_text": document.text,
        "fields": {},
        "line_items": [],
        "vat_breakdown": [],
        "all_entities": [],
        "annotations": [],  # Bounding boxes for overlay display
    }

    # Get page dimensions
    page_width = 1
    page_height = 1
    if document.pages:
        page = document.pages[0]
        if page.dimension:
            page_width = page.dimension.width
            page_height = page.dimension.height
    result["page_dimensions"] = {"width": page_width, "height": page_height}

    for entity in document.entities:
        bbox = _get_bounding_box(entity)

        entry = {
            "type": entity.type_,
            "value": entity.mention_text,
            "confidence": round(entity.confidence, 3),
        }

        # Short labels for overlay display
        SHORT_LABELS = {
            "supplier_name": "Vendor",
            "supplier_address": "Addr",
            "supplier_phone": "Phone",
            "supplier_email": "Email",
            "supplier_tax_id": "Tax ID",
            "supplier_iban": "IBAN",
            "supplier_website": "Web",
            "supplier_registration": "Reg#",
            "supplier_payment_ref": "Pay Ref",
            "receiver_name": "Bill To",
            "receiver_address": "Cust Addr",
            "receiver_tax_id": "Cust Tax ID",
            "receiver_email": "Cust Email",
            "receiver_phone": "Cust Phone",
            "invoice_id": "Inv#",
            "invoice_date": "Date",
            "invoice_type": "Type",
            "due_date": "Due",
            "delivery_date": "Delivery",
            "purchase_order": "PO#",
            "payment_terms": "Terms",
            "currency": "Cur",
            "currency_exchange_rate": "FX Rate",
            "net_amount": "Subtotal",
            "total_amount": "Total",
            "total_tax_amount": "Tax",
            "freight_amount": "Ship",
            "amount_paid_since_last_invoice": "Paid",
            "remit_to_name": "Remit",
            "remit_to_address": "Remit Addr",
            "ship_to_name": "Ship To",
            "ship_to_address": "Ship Addr",
            "ship_from_name": "Ship From",
            "ship_from_address": "From Addr",
            "carrier": "Carrier",
            "line_item/description": "Item",
            "line_item/quantity": "Qty",
            "line_item/unit_price": "Price",
            "line_item/amount": "Amt",
            "line_item/product_code": "Code",
            "line_item/unit": "Unit",
            "line_item/purchase_order": "PO",
        }

        # Store annotation for overlay
        if bbox and entity.type_ not in ("line_item", "vat"):
            result["annotations"].append({
                "type": entity.type_,
                "label": SHORT_LABELS.get(entity.type_, entity.type_.replace("_", " ")[:12]),
                "value": entity.mention_text,
                "bbox": bbox,
                "confidence": round(entity.confidence, 3),
            })

        if entity.type_ == "line_item" and entity.properties:
            line_item = {}
            for prop in entity.properties:
                prop_bbox = _get_bounding_box(prop)
                line_item[prop.type_] = {
                    "value": prop.mention_text,
                    "confidence": round(prop.confidence, 3),
                }
                if prop_bbox:
                    full_type = f"line_item/{prop.type_}"
                    result["annotations"].append({
                        "type": full_type,
                        "label": SHORT_LABELS.get(full_type, prop.type_.replace("_", " ")[:8]),
                        "value": prop.mention_text,
                        "bbox": prop_bbox,
                        "confidence": round(prop.confidence, 3),
                    })
            entry["properties"] = line_item
            result["line_items"].append(line_item)

        elif entity.type_ == "vat" and entity.properties:
            vat_entry = {}
            for prop in entity.properties:
                vat_entry[prop.type_] = {
                    "value": prop.mention_text,
                    "confidence": round(prop.confidence, 3),
                }
            entry["properties"] = vat_entry
            result["vat_breakdown"].append(vat_entry)

        elif entity.properties:
            for prop in entity.properties:
                key = f"{entity.type_}/{prop.type_}"
                result["fields"][key] = {
                    "value": prop.mention_text,
                    "confidence": round(prop.confidence, 3),
                }

        else:
            result["fields"][entity.type_] = {
                "value": entity.mention_text,
                "confidence": round(entity.confidence, 3),
            }

        result["all_entities"].append(entry)

    return result


def _build_grounding_text(invoice_id: str, data: dict) -> str:
    """Build a natural-language grounding context from Document AI extraction.

    This text is injected into the live agent session so the agent has
    verified, structured data to reference — not just what it "sees".
    """
    lines = [f"[GROUNDED INVOICE DATA — ID: {invoice_id}]"]
    lines.append("The following data was extracted by Google Document AI with confidence scores.")
    lines.append("Use this as your source of truth. Do NOT guess or hallucinate values.")
    lines.append("")

    fields = data.get("fields", {})

    # Complete Document AI Invoice Parser field schema
    # See: https://docs.cloud.google.com/document-ai/docs/processors-list
    field_labels = {
        # ── Invoice identification ──
        "invoice_id": "Invoice Number",
        "invoice_date": "Invoice Date",
        "invoice_type": "Invoice Type",
        "due_date": "Due Date",
        "delivery_date": "Delivery Date",
        "purchase_order": "Purchase Order #",
        "payment_terms": "Payment Terms",
        "currency": "Currency",
        "currency_exchange_rate": "Exchange Rate",
        # ── Supplier/Vendor ──
        "supplier_name": "Vendor/Supplier",
        "supplier_address": "Vendor Address",
        "supplier_phone": "Vendor Phone",
        "supplier_email": "Vendor Email",
        "supplier_website": "Vendor Website",
        "supplier_tax_id": "Vendor Tax ID",
        "supplier_iban": "Vendor IBAN",
        "supplier_registration": "Vendor Registration #",
        "supplier_payment_ref": "Payment Reference",
        # ── Receiver/Customer ──
        "receiver_name": "Bill To (Customer)",
        "receiver_address": "Customer Address",
        "receiver_email": "Customer Email",
        "receiver_phone": "Customer Phone",
        "receiver_website": "Customer Website",
        "receiver_tax_id": "Customer Tax ID",
        # ── Shipping ──
        "ship_to_name": "Ship To",
        "ship_to_address": "Ship To Address",
        "ship_from_name": "Ship From",
        "ship_from_address": "Ship From Address",
        "carrier": "Carrier/Shipping Method",
        "freight_amount": "Freight/Shipping Amount",
        # ── Remittance ──
        "remit_to_name": "Remit To",
        "remit_to_address": "Remit To Address",
        # ── Amounts ──
        "net_amount": "Subtotal (Net)",
        "total_tax_amount": "Total Tax",
        "total_amount": "Total Amount Due",
        "amount_paid_since_last_invoice": "Amount Already Paid",
        # ── VAT breakdown (nested) ──
        "vat/amount": "VAT Taxable Amount",
        "vat/tax_amount": "VAT Tax Amount",
        "vat/tax_rate": "VAT Rate",
        "vat/category_code": "VAT Category Code",
    }

    lines.append("## Key Fields")
    for field_type, field_data in fields.items():
        label = field_labels.get(field_type, field_type.replace("_", " ").title())
        conf = field_data["confidence"]
        conf_tag = "HIGH" if conf >= 0.9 else "MEDIUM" if conf >= 0.7 else "LOW"
        lines.append(f"- {label}: {field_data['value']} (confidence: {conf} [{conf_tag}])")

    line_items = data.get("line_items", [])
    if line_items:
        lines.append("")
        lines.append(f"## Line Items ({len(line_items)} items)")
        for i, item in enumerate(line_items, 1):
            parts = []
            for prop_type, prop_data in item.items():
                prop_label = prop_type.replace("line_item/", "").replace("_", " ").title()
                parts.append(f"{prop_label}: {prop_data['value']}")
            lines.append(f"  {i}. {' | '.join(parts)}")

    # VAT breakdown (multiple rates on same invoice)
    vat_breakdown = data.get("vat_breakdown", [])
    if vat_breakdown:
        lines.append("")
        lines.append(f"## VAT/Tax Breakdown ({len(vat_breakdown)} rates)")
        for i, vat in enumerate(vat_breakdown, 1):
            parts = []
            for prop_type, prop_data in vat.items():
                prop_label = prop_type.replace("vat/", "").replace("_", " ").title()
                parts.append(f"{prop_label}: {prop_data['value']}")
            lines.append(f"  {i}. {' | '.join(parts)}")

    # Flag low-confidence fields
    low_conf = [
        (field_labels.get(ft, ft), fd["value"], fd["confidence"])
        for ft, fd in fields.items()
        if fd["confidence"] < 0.7
    ]
    if low_conf:
        lines.append("")
        lines.append("## Low Confidence Fields (ask user to verify)")
        for label, value, conf in low_conf:
            lines.append(f"- {label}: '{value}' (confidence: {conf}) — PLEASE VERIFY WITH USER")

    lines.append("")
    lines.append("[END GROUNDED DATA]")
    return "\n".join(lines)


# ── Public Functions ──────────────────────────────────────────────────────


def process_invoice_on_upload(invoice_id: str) -> dict:
    """Process an invoice with Document AI immediately on upload.

    Called by the upload endpoint. Returns extracted data + grounding text.
    If Document AI is not configured, returns None (agent falls back to vision).
    """
    if not DOCAI_ENABLED:
        logger.info("Document AI not configured — agent will use vision only")
        return None

    if invoice_id not in invoice_store:
        logger.error(f"Invoice {invoice_id} not in store")
        return None

    invoice = invoice_store[invoice_id]

    try:
        extracted = _call_document_ai(invoice["image_bytes"], invoice["mime_type"])
        grounding = _build_grounding_text(invoice_id, extracted)

        # Store results
        invoice["extracted_data"] = extracted
        invoice["grounding_text"] = grounding

        logger.info(
            f"Document AI processed invoice {invoice_id}: "
            f"{len(extracted['fields'])} fields, {len(extracted['line_items'])} line items"
        )

        return {
            "extracted_data": extracted,
            "grounding_text": grounding,
        }

    except Exception as e:
        logger.error(f"Document AI failed for {invoice_id}: {e}")
        return None


# ── Agent Tools ───────────────────────────────────────────────────────────


def parse_invoice(invoice_id: str) -> dict:
    """Extract structured data from an invoice using Google Document AI.

    Call this tool to get accurate, grounded data from a scanned invoice.
    Returns field-by-field extraction with confidence scores.

    Args:
        invoice_id: The ID of the uploaded invoice to parse.

    Returns:
        Dictionary with extracted fields, line items, and confidence scores.
    """
    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found. Ask the user to upload one first."}

    invoice = invoice_store[invoice_id]

    # If already processed, return cached data
    if "extracted_data" in invoice:
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "fields": invoice["extracted_data"]["fields"],
            "line_items": invoice["extracted_data"]["line_items"],
        }

    if not DOCAI_ENABLED:
        return {
            "status": "docai_not_configured",
            "message": (
                "Document AI is not configured. I'll analyze the invoice visually. "
                "Note: visual analysis may be less accurate than Document AI grounding."
            ),
        }

    # Process now if not already done
    result = process_invoice_on_upload(invoice_id)
    if result:
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "fields": result["extracted_data"]["fields"],
            "line_items": result["extracted_data"]["line_items"],
        }

    return {"status": "error", "message": "Document AI processing failed."}


def get_invoice_data(invoice_id: str) -> dict:
    """Retrieve previously extracted data for an invoice.

    Args:
        invoice_id: The ID of the invoice.

    Returns:
        The extracted invoice data, or an error if not found.
    """
    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    if "extracted_data" not in invoice:
        return {"message": "No structured data yet. Use parse_invoice first, or upload a new scan."}

    return {
        "invoice_id": invoice_id,
        "fields": invoice["extracted_data"]["fields"],
        "line_items": invoice["extracted_data"]["line_items"],
        "full_text": invoice["extracted_data"]["full_text"],
    }


def export_invoice_json(invoice_id: str) -> str:
    """Export extracted invoice data as formatted JSON for download.

    Args:
        invoice_id: The ID of the invoice to export.

    Returns:
        JSON string of the extracted data.
    """
    if invoice_id not in invoice_store:
        return json.dumps({"error": f"Invoice '{invoice_id}' not found."})

    invoice = invoice_store[invoice_id]
    data = invoice.get("extracted_data", {})

    if not data:
        return json.dumps({"message": "No data extracted yet."})

    # Build clean export
    export = {
        "invoice_id": invoice_id,
        "fields": {
            k: v["value"] for k, v in data.get("fields", {}).items()
        },
        "line_items": [
            {k.replace("line_item/", ""): v["value"] for k, v in item.items()}
            for item in data.get("line_items", [])
        ],
        "full_text": data.get("full_text", ""),
    }

    return json.dumps(export, indent=2)
