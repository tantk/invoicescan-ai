"""Smart extraction — confidence-based auto-escalation and XML parsing.

Three enhancements to the extraction pipeline:

1. CONFIDENCE ESCALATION — if Document AI returns low confidence on key
   fields, automatically trigger Gemini Vision to double-check.

2. SMART OCR FALLBACK — if Document AI fails entirely (blurry image,
   unsupported format), fall back to Gemini Vision for full extraction.

3. E-INVOICE XML PARSING — if the uploaded file is structured XML
   (UBL, CII, ZUGFeRD), parse it directly — 100% accurate, no OCR.
"""

import json
import logging
import re
from typing import Optional
from xml.etree import ElementTree

logger = logging.getLogger(__name__)

# Fields that matter most — trigger escalation if these are low confidence
CRITICAL_FIELDS = {
    "total_amount", "net_amount", "total_tax_amount",
    "invoice_id", "invoice_date", "supplier_name", "supplier_tax_id",
}

CONFIDENCE_THRESHOLD = 0.75  # Below this → ask Gemini to double-check


def check_confidence_and_escalate(invoice_id: str) -> dict:
    """Check Document AI confidence scores and escalate low-confidence fields to Gemini Vision.

    If any critical field has confidence below threshold, Gemini Vision
    re-reads those specific fields from the image for a second opinion.
    If both agree, confidence increases. If they disagree, flag for user review.

    Args:
        invoice_id: The invoice to check.

    Returns:
        Escalation results — which fields were re-checked, any disagreements.
    """
    from .invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    extracted = invoice.get("extracted_data", {})
    fields = extracted.get("fields", {})

    if not fields:
        return {"status": "no_data", "message": "No extracted data to check."}

    # Find low-confidence critical fields
    low_confidence = []
    for field_name in CRITICAL_FIELDS:
        if field_name in fields:
            field = fields[field_name]
            conf = field.get("confidence", 1.0) if isinstance(field, dict) else 1.0
            if conf < CONFIDENCE_THRESHOLD:
                low_confidence.append({
                    "field": field_name,
                    "value": field.get("value", "") if isinstance(field, dict) else str(field),
                    "confidence": conf,
                })

    if not low_confidence:
        return {
            "status": "all_confident",
            "message": "All critical fields have high confidence. No escalation needed.",
            "checked_fields": len(CRITICAL_FIELDS & set(fields.keys())),
        }

    # Escalate to Gemini Vision for re-extraction
    fields_to_recheck = [lc["field"] for lc in low_confidence]
    logger.info(f"Escalating {len(fields_to_recheck)} low-confidence fields to Gemini Vision: {fields_to_recheck}")

    from .custom_extractor import extract_custom_fields

    gemini_result = extract_custom_fields(
        invoice_id=invoice_id,
        fields_to_extract=fields_to_recheck,
        context="Re-checking low-confidence fields from Document AI. Be precise.",
    )

    if gemini_result.get("status") != "success":
        return {
            "status": "escalation_failed",
            "low_confidence_fields": low_confidence,
            "message": "Gemini Vision re-check failed. Manual verification recommended.",
        }

    # Compare Document AI vs Gemini results
    gemini_fields = gemini_result.get("fields_found", {})
    comparisons = []

    for lc in low_confidence:
        field_name = lc["field"]
        docai_value = lc["value"]
        gemini_value = gemini_fields.get(field_name)

        if gemini_value is None:
            comparisons.append({
                "field": field_name,
                "docai_value": docai_value,
                "gemini_value": None,
                "status": "GEMINI_NOT_FOUND",
                "action": "Keep Document AI value, flag for user review.",
            })
        elif str(gemini_value).strip().lower() == str(docai_value).strip().lower():
            comparisons.append({
                "field": field_name,
                "docai_value": docai_value,
                "gemini_value": gemini_value,
                "status": "AGREE",
                "action": "Both agree — value is likely correct despite low Doc AI confidence.",
            })
        else:
            comparisons.append({
                "field": field_name,
                "docai_value": docai_value,
                "gemini_value": gemini_value,
                "status": "DISAGREE",
                "action": "Document AI and Gemini disagree — ASK THE USER to verify.",
            })

    disagreements = [c for c in comparisons if c["status"] == "DISAGREE"]

    return {
        "status": "escalated",
        "fields_checked": len(comparisons),
        "agreements": len([c for c in comparisons if c["status"] == "AGREE"]),
        "disagreements": len(disagreements),
        "comparisons": comparisons,
        "needs_user_review": len(disagreements) > 0,
    }


def parse_einvoice_xml(xml_content: str) -> Optional[dict]:
    """Parse a structured e-invoice XML (UBL, CII, ZUGFeRD).

    If the uploaded file is XML, this extracts data with 100% accuracy —
    no OCR needed. Handles the major e-invoice formats.

    Args:
        xml_content: The XML string content.

    Returns:
        Extracted fields dict, or None if not a recognized e-invoice format.
    """
    try:
        root = ElementTree.fromstring(xml_content)
    except ElementTree.ParseError:
        return None

    tag = root.tag.lower()
    ns = re.match(r"\{(.+?)\}", root.tag)
    namespace = ns.group(1) if ns else ""

    # Detect format
    if "invoice" in tag and ("oasis" in namespace or "ubl" in namespace):
        return _parse_ubl_invoice(root)
    elif "crossindustryinvoice" in tag or "cii" in namespace:
        return _parse_cii_invoice(root)
    elif "fatturapa" in tag or "fattura" in namespace:
        return _parse_fatturapa(root)

    logger.info(f"Unrecognized XML format: tag={root.tag}")
    return None


def _ns_find(element, path, namespaces=None):
    """Find element text with namespace-agnostic fallback."""
    # Try with namespace
    result = element.find(path, namespaces)
    if result is not None:
        return result.text.strip() if result.text else ""

    # Try without namespace (strip all ns prefixes)
    simple_path = re.sub(r"\{[^}]+\}", "", path)
    for child in element.iter():
        simple_tag = re.sub(r"\{[^}]+\}", "", child.tag)
        if simple_tag == simple_path.split("/")[-1]:
            return child.text.strip() if child.text else ""

    return ""


def _parse_ubl_invoice(root) -> dict:
    """Parse UBL 2.1 Invoice (Peppol BIS, XRechnung, etc.)."""
    ns = {"ubl": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
          "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
          "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}

    fields = {}
    fields["invoice_id"] = _ns_find(root, ".//cbc:ID", ns) or _ns_find(root, ".//ID")
    fields["invoice_date"] = _ns_find(root, ".//cbc:IssueDate", ns) or _ns_find(root, ".//IssueDate")
    fields["due_date"] = _ns_find(root, ".//cbc:DueDate", ns) or _ns_find(root, ".//DueDate")
    fields["currency"] = _ns_find(root, ".//cbc:DocumentCurrencyCode", ns) or _ns_find(root, ".//DocumentCurrencyCode")

    # Supplier
    supplier = root.find(".//cac:AccountingSupplierParty", ns)
    if supplier is None:
        supplier = root.find(".//{*}AccountingSupplierParty")
    if supplier is not None:
        fields["supplier_name"] = _ns_find(supplier, ".//cbc:Name", ns) or _ns_find(supplier, ".//Name")
        fields["supplier_tax_id"] = _ns_find(supplier, ".//cbc:CompanyID", ns) or _ns_find(supplier, ".//CompanyID")

    # Receiver
    customer = root.find(".//cac:AccountingCustomerParty", ns)
    if customer is None:
        customer = root.find(".//{*}AccountingCustomerParty")
    if customer is not None:
        fields["receiver_name"] = _ns_find(customer, ".//cbc:Name", ns) or _ns_find(customer, ".//Name")
        fields["receiver_tax_id"] = _ns_find(customer, ".//cbc:CompanyID", ns) or _ns_find(customer, ".//CompanyID")

    # Totals
    monetary = root.find(".//cac:LegalMonetaryTotal", ns)
    if monetary is None:
        monetary = root.find(".//{*}LegalMonetaryTotal")
    if monetary is not None:
        fields["net_amount"] = _ns_find(monetary, ".//cbc:TaxExclusiveAmount", ns) or _ns_find(monetary, ".//TaxExclusiveAmount")
        fields["total_amount"] = _ns_find(monetary, ".//cbc:PayableAmount", ns) or _ns_find(monetary, ".//PayableAmount")

    # Tax
    tax_total = root.find(".//cac:TaxTotal", ns)
    if tax_total is None:
        tax_total = root.find(".//{*}TaxTotal")
    if tax_total is not None:
        fields["total_tax_amount"] = _ns_find(tax_total, ".//cbc:TaxAmount", ns) or _ns_find(tax_total, ".//TaxAmount")

    # Line items
    line_items = []
    for line in root.findall(".//cac:InvoiceLine", ns) or root.findall(".//{*}InvoiceLine"):
        item = {}
        item["line_item/description"] = _ns_find(line, ".//cbc:Name", ns) or _ns_find(line, ".//Name")
        item["line_item/quantity"] = _ns_find(line, ".//cbc:InvoicedQuantity", ns) or _ns_find(line, ".//InvoicedQuantity")
        item["line_item/amount"] = _ns_find(line, ".//cbc:LineExtensionAmount", ns) or _ns_find(line, ".//LineExtensionAmount")
        item["line_item/unit_price"] = _ns_find(line, ".//cbc:PriceAmount", ns) or _ns_find(line, ".//PriceAmount")
        line_items.append({k: {"value": v, "confidence": 1.0} for k, v in item.items() if v})

    # Clean empty fields
    fields = {k: {"value": v, "confidence": 1.0} for k, v in fields.items() if v}

    return {
        "fields": fields,
        "line_items": line_items,
        "vat_breakdown": [],
        "full_text": "",
        "source": "e-invoice XML (UBL)",
    }


def _parse_cii_invoice(root) -> dict:
    """Parse CII (Cross Industry Invoice) format."""
    fields = {}

    # Basic extraction — CII has deep nesting
    for elem in root.iter():
        tag = re.sub(r"\{[^}]+\}", "", elem.tag)
        text = elem.text.strip() if elem.text else ""
        if not text:
            continue

        if tag == "ID" and "invoice_id" not in fields:
            fields["invoice_id"] = text
        elif tag == "DateTimeString" and "invoice_date" not in fields:
            fields["invoice_date"] = text
        elif tag == "Name" and "supplier_name" not in fields:
            fields["supplier_name"] = text
        elif tag in ("GrandTotalAmount", "DuePayableAmount") and "total_amount" not in fields:
            fields["total_amount"] = text
        elif tag == "TaxTotalAmount" and "total_tax_amount" not in fields:
            fields["total_tax_amount"] = text
        elif tag in ("TaxBasisTotalAmount", "LineTotalAmount") and "net_amount" not in fields:
            fields["net_amount"] = text

    fields = {k: {"value": v, "confidence": 1.0} for k, v in fields.items() if v}

    return {
        "fields": fields,
        "line_items": [],
        "vat_breakdown": [],
        "full_text": "",
        "source": "e-invoice XML (CII)",
    }


def _parse_fatturapa(root) -> dict:
    """Parse Italian FatturaPA XML."""
    fields = {}

    for elem in root.iter():
        tag = re.sub(r"\{[^}]+\}", "", elem.tag)
        text = elem.text.strip() if elem.text else ""
        if not text:
            continue

        if tag == "Numero":
            fields["invoice_id"] = text
        elif tag == "Data":
            fields["invoice_date"] = text
        elif tag == "Denominazione" and "supplier_name" not in fields:
            fields["supplier_name"] = text
        elif tag == "ImportoTotaleDocumento":
            fields["total_amount"] = text
        elif tag == "IdCodice" and "supplier_tax_id" not in fields:
            fields["supplier_tax_id"] = text

    fields = {k: {"value": v, "confidence": 1.0} for k, v in fields.items() if v}

    return {
        "fields": fields,
        "line_items": [],
        "vat_breakdown": [],
        "full_text": "",
        "source": "e-invoice XML (FatturaPA)",
    }
