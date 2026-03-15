"""Dynamic field extraction using Gemini Vision.

Layer 2 of the extraction pipeline:
  Layer 1: Document AI Invoice Parser → 46 standard fields (always runs)
  Layer 2: Gemini Vision → custom fields on demand (this module)

The agent detects the invoice type (country, industry) and decides what
additional fields to look for. It calls extract_custom_fields() with a
list of field names, and Gemini reads the image to find them.

This is the key differentiator: the agent adaptively extracts what it
needs based on context, without pre-training or uptraining.
"""

import json
import logging
from typing import Optional

from google import genai
from google.genai import types as genai_types

from ..config import GCP_PROJECT, GCP_LOCATION

logger = logging.getLogger(__name__)

# ── Industry-specific field sets ──────────────────────────────────────────
# The agent can use these as suggestions, or specify its own fields.

INDUSTRY_FIELDS = {
    "construction": {
        "fields": [
            "retainage_percentage",
            "retainage_amount",
            "contract_sum",
            "change_order_amount",
            "net_change_by_change_orders",
            "percent_complete",
            "total_completed_and_stored",
            "previous_certificates_amount",
            "current_payment_due",
            "balance_to_finish",
            "architect_name",
            "project_name",
            "project_number",
            "application_number",
            "contractor_license_number",
        ],
        "description": "Construction invoice (AIA G702/G703, progress billing)",
    },
    "healthcare": {
        "fields": [
            "patient_name",
            "patient_id",
            "patient_dob",
            "insurance_provider",
            "insurance_policy_number",
            "insurance_group_number",
            "prior_authorization_number",
            "referring_physician",
            "referring_physician_npi",
            "rendering_provider_npi",
            "place_of_service_code",
            "diagnosis_codes",  # ICD-10
            "procedure_codes",  # CPT/HCPCS
            "modifier_codes",
            "copay_amount",
            "coinsurance_amount",
            "deductible_amount",
            "allowed_amount",
        ],
        "description": "Healthcare invoice/claim (CMS-1500, UB-04)",
    },
    "legal": {
        "fields": [
            "matter_number",
            "matter_name",
            "client_matter_id",
            "responsible_attorney",
            "timekeeper_name",
            "timekeeper_title",
            "timekeeper_rate",
            "hours_worked",
            "task_code",
            "activity_code",
            "expense_type",
            "billing_period_start",
            "billing_period_end",
            "trust_account_balance",
            "retainer_balance",
        ],
        "description": "Legal invoice (LEDES, billable hours)",
    },
    "freight": {
        "fields": [
            "bill_of_lading_number",
            "pro_number",
            "container_number",
            "seal_number",
            "vessel_name",
            "voyage_number",
            "port_of_loading",
            "port_of_discharge",
            "actual_weight",
            "volumetric_weight",
            "chargeable_weight",
            "fuel_surcharge",
            "demurrage_charges",
            "detention_charges",
            "accessorial_charges",
            "incoterms",
            "commodity_code",
            "number_of_packages",
        ],
        "description": "Freight/logistics invoice (BOL, shipping)",
    },
    "saas": {
        "fields": [
            "subscription_id",
            "plan_name",
            "plan_tier",
            "billing_period_start",
            "billing_period_end",
            "number_of_seats",
            "per_seat_price",
            "usage_metric",
            "usage_quantity",
            "overage_quantity",
            "overage_rate",
            "prorated_amount",
            "credit_applied",
            "next_renewal_date",
        ],
        "description": "SaaS/subscription invoice (usage-based, per-seat)",
    },
    "hospitality": {
        "fields": [
            "guest_name",
            "room_number",
            "room_type",
            "checkin_date",
            "checkout_date",
            "number_of_nights",
            "nightly_rate",
            "room_charges_total",
            "food_and_beverage_total",
            "minibar_charges",
            "spa_charges",
            "parking_charges",
            "occupancy_tax",
            "city_tax",
            "tourism_tax",
            "resort_fee",
            "service_charge_percentage",
            "service_charge_amount",
            "folio_number",
        ],
        "description": "Hotel/hospitality folio",
    },
    "manufacturing": {
        "fields": [
            "part_number",
            "lot_number",
            "batch_number",
            "serial_number",
            "heat_number",
            "material_grade",
            "hs_tariff_code",
            "country_of_origin",
            "net_weight",
            "gross_weight",
            "inspection_certificate_number",
            "bom_reference",
        ],
        "description": "Manufacturing invoice (BOM, lot tracking)",
    },
    "gst_india": {
        "fields": [
            "gstin_supplier",
            "gstin_buyer",
            "place_of_supply",
            "state_code",
            "hsn_code",
            "sac_code",
            "cgst_rate",
            "cgst_amount",
            "sgst_rate",
            "sgst_amount",
            "igst_rate",
            "igst_amount",
            "cess_rate",
            "cess_amount",
            "reverse_charge",
            "irn_number",
            "e_way_bill_number",
            "total_in_words",
        ],
        "description": "Indian GST invoice (CGST/SGST/IGST breakdown)",
    },
    "eu_vat": {
        "fields": [
            "seller_vat_number",
            "buyer_vat_number",
            "reverse_charge_indicator",
            "intra_community_supply",
            "vat_directive_reference",
            "vat_rate_1",
            "vat_amount_1",
            "vat_taxable_base_1",
            "vat_rate_2",
            "vat_amount_2",
            "vat_taxable_base_2",
        ],
        "description": "EU VAT invoice (reverse charge, intra-community)",
    },
    "trade_terms": {
        "fields": [
            "incoterm",
            "incoterm_location",
            "shipping_method",
            "port_of_loading",
            "port_of_discharge",
            "country_of_origin",
            "hs_tariff_code",
            "customs_declaration_number",
            "export_license_number",
            "certificate_of_origin",
            "insurance_value",
            "freight_charges",
            "duty_amount",
            "import_permit_number",
        ],
        "description": "International trade invoice (Incoterms, customs, duties)",
    },
    "payment_banking": {
        "fields": [
            "payment_method",
            "payment_method_code",
            "early_payment_discount_terms",
            "early_payment_discount_percentage",
            "early_payment_discount_due_date",
            "bank_name",
            "bank_account_number",
            "iban",
            "swift_bic",
            "routing_number",
            "sort_code",
            "payment_reference",
            "remittance_information",
            "letter_of_credit_number",
            "direct_debit_mandate_id",
            "factoring_assignment_notice",
        ],
        "description": "Payment details and banking references on invoices",
    },
    "discounts_charges": {
        "fields": [
            "trade_discount_percentage",
            "trade_discount_amount",
            "volume_discount",
            "early_payment_discount",
            "promotional_discount",
            "handling_fee",
            "packaging_charge",
            "insurance_charge",
            "fuel_surcharge",
            "environmental_fee",
            "restocking_fee",
            "rush_fee",
            "minimum_order_surcharge",
            "credit_card_surcharge",
            "late_payment_interest_rate",
            "late_payment_penalty",
            "service_charge_percentage",
            "service_charge_amount",
            "gratuity",
        ],
        "description": "All discounts, charges, fees, and surcharges on an invoice",
    },
    "po_matching": {
        "fields": [
            "purchase_order_number",
            "sales_order_number",
            "delivery_note_number",
            "goods_received_note",
            "packing_slip_number",
            "contract_number",
            "work_order_number",
            "job_number",
            "project_number",
            "requisition_number",
            "return_authorization_rma",
            "proforma_invoice_reference",
            "credit_note_reference",
            "tender_bid_reference",
        ],
        "description": "PO matching and document cross-references",
    },
    "certifications": {
        "fields": [
            "iso_certification",
            "mill_test_report_number",
            "certificate_of_conformity",
            "certificate_of_analysis",
            "certificate_of_origin",
            "inspection_certificate_number",
            "material_grade",
            "en_10204_certificate_type",
            "batch_lot_number",
            "serial_numbers",
            "calibration_certificate",
            "msds_sds_reference",
            "organic_certification",
            "fair_trade_certification",
        ],
        "description": "Quality certificates and compliance references on invoices",
    },
    "product_codes": {
        "fields": [
            "hs_code",
            "hsn_code",
            "sac_code",
            "unspsc_code",
            "gtin_ean_upc",
            "sku_part_number",
            "manufacturer_part_number",
            "ndc_code",
            "cas_number",
            "un_dangerous_goods_number",
            "cpv_code",
        ],
        "description": "Product classification codes (HS, UNSPSC, GTIN, NDC, etc.)",
    },
    "line_item_details": {
        "fields": [
            "line_items_with_tax",
        ],
        "description": "Detailed line items with per-item tax rates, categories, and amounts",
    },
}


# ── OCR Text Position Matching ────────────────────────────────────────────


def _find_text_in_ocr(invoice: dict, search_text: str) -> Optional[list]:
    """Find text in Document AI's OCR data and return its bounding box.

    Searches the Document AI page layout for the given text.
    Returns [[x1,y1],[x2,y1],[x2,y2],[x1,y2]] normalized coords, or None.
    """
    try:
        extracted = invoice.get("extracted_data", {})
        full_text = extracted.get("full_text", "")

        if not full_text or not search_text:
            return None

        # Find the text position in the OCR string
        search_lower = search_text.lower().strip()
        text_lower = full_text.lower()
        idx = text_lower.find(search_lower)

        if idx < 0:
            # Try partial match (first significant word)
            words = search_lower.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 3:
                        idx = text_lower.find(word)
                        if idx >= 0:
                            break

        if idx < 0:
            return None

        # Now find which annotation from Document AI covers this text position
        # Check existing annotations for overlapping text
        for ann in extracted.get("annotations", []):
            ann_value = ann.get("value", "").lower().strip()
            if search_lower in ann_value or ann_value in search_lower:
                return ann.get("bbox")

        # If no annotation matches, try to find in all_entities
        for entity in extracted.get("all_entities", []):
            entity_value = entity.get("value", "").lower().strip()
            if search_lower in entity_value or entity_value in search_lower:
                # This entity matched but may not have bbox in our data
                # Return None — let Gemini fallback handle it
                break

        return None

    except Exception:
        return None


# ── Gemini Vision Extraction ─────────────────────────────────────────────


def _build_extraction_prompt(fields: list[str], context: str = "") -> str:
    """Build a structured extraction prompt for Gemini."""

    # Special handling for line item detail extraction
    if fields == ["line_items_with_tax"]:
        return f"""Analyze this invoice image and extract ALL line items with their individual tax details.

{f"Context: {context}" if context else ""}

For EACH line item, extract:
- description: what the item is
- quantity: how many
- unit_price: price per unit
- amount: total for this line (before tax)
- tax_rate: the tax rate applied to THIS specific item (e.g., "10%", "8%", "0%")
- tax_amount: the tax amount for this item
- tax_category: if marked (e.g., "standard", "reduced", "exempt", "zero-rated")

Return a JSON object with a "line_items" array. Example:
{{"line_items": [
  {{"description": "Software Dev", "quantity": "1", "unit_price": "500000", "amount": "500000", "tax_rate": "10%", "tax_amount": "50000", "tax_category": "standard"}},
  {{"description": "Lunch boxes", "quantity": "10", "unit_price": "1000", "amount": "10000", "tax_rate": "8%", "tax_amount": "800", "tax_category": "reduced"}}
]}}

Return ONLY valid JSON. Extract what is clearly visible. If a field is not visible, set to null."""

    field_list = "\n".join(f"- {f}" for f in fields)

    return f"""Analyze this invoice image and extract the following specific fields.
For each field, return the value AND the approximate bounding box location on the image.
Bounding box should be normalized coordinates (0-1 range): [x_min, y_min, x_max, y_max]
where (0,0) is top-left and (1,1) is bottom-right.

If a field is not found in the invoice, set its value to null.
Do NOT guess or hallucinate values — only extract what is clearly visible.

{f"Context: {context}" if context else ""}

Fields to extract:
{field_list}

Return ONLY valid JSON. Example:
{{"field_name": {{"value": "extracted value", "bbox": [0.1, 0.2, 0.4, 0.25]}}, "other_field": null}}"""


def extract_custom_fields(
    invoice_id: str,
    fields_to_extract: list[str],
    context: str = "",
) -> dict:
    """Extract custom fields from an invoice using Gemini Vision.

    Use this when you need fields beyond Document AI's standard 46 fields.
    Specify exactly which fields to look for based on the invoice type.

    For industry-specific fields, you can use these preset groups:
    - "construction": retainage, contract sum, % complete, AIA fields
    - "healthcare": CPT codes, NPI, diagnosis codes, insurance info
    - "legal": matter number, timekeeper, billable hours, LEDES
    - "freight": BOL, container, weight, demurrage, incoterms
    - "saas": subscription, seats, usage, proration
    - "hospitality": room, folio, occupancy tax, service charge
    - "manufacturing": lot/serial numbers, BOM, HS codes
    - "gst_india": CGST, SGST, IGST, HSN/SAC codes, IRN
    - "eu_vat": VAT numbers, reverse charge, intra-community

    Or specify any custom field names — Gemini will look for them.

    Args:
        invoice_id: The ID of the uploaded invoice.
        fields_to_extract: List of field names to extract, OR a single
                          industry preset name (e.g., "construction").
        context: Optional hint about the invoice type for better accuracy.

    Returns:
        Dictionary with extracted custom fields and their values.
    """
    from .invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]

    # Handle industry preset names
    if len(fields_to_extract) == 1 and fields_to_extract[0] in INDUSTRY_FIELDS:
        preset = INDUSTRY_FIELDS[fields_to_extract[0]]
        fields_to_extract = preset["fields"]
        if not context:
            context = preset["description"]

    try:
        client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT,
            location=GCP_LOCATION,
        )

        # Build image part
        image_part = genai_types.Part.from_bytes(
            data=invoice["image_bytes"],
            mime_type=invoice["mime_type"],
        )

        prompt = _build_extraction_prompt(fields_to_extract, context)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image_part, prompt],
            config=genai_types.GenerateContentConfig(
                temperature=0.1,  # Low temp for accurate extraction
                response_mime_type="application/json",
            ),
        )

        # Parse JSON response
        raw_text = response.text.strip()
        # Remove markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3].strip()

        extracted = json.loads(raw_text)

        # Handle line_items_with_tax response (array, not flat dict)
        if "line_items" in extracted:
            line_items = extracted["line_items"]
            invoice["custom_line_items"] = line_items

            # Push detailed line items to Sheets
            try:
                from .sheets import _get_client, _get_or_create_worksheet, _ensure_columns, _format_headers, _extract_value
                from ..config import SHEETS_ENABLED, SHEETS_SPREADSHEET_ID
                if SHEETS_ENABLED:
                    client = _get_client()
                    spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)
                    headers = ["Scan ID", "Item #", "Description", "Quantity", "Unit Price", "Amount", "Tax Rate", "Tax Amount", "Tax Category"]
                    ws = _get_or_create_worksheet(spreadsheet, "Line Items", headers)
                    current_headers = ws.row_values(1)
                    if not current_headers:
                        current_headers = headers
                        ws.update("A1", [current_headers])
                        _format_headers(ws, len(current_headers))
                    else:
                        current_headers = _ensure_columns(ws, current_headers, headers)

                    rows = []
                    for i, item in enumerate(line_items, 1):
                        row = [invoice_id, str(i)]
                        for h in current_headers[2:]:
                            key = h.lower().replace(" ", "_")
                            row.append(str(item.get(key, "") or ""))
                        rows.append(row)
                    if rows:
                        ws.append_rows(rows, value_input_option="USER_ENTERED")
                        logger.info(f"Updated {len(rows)} line items with tax details for {invoice_id}")
            except Exception as e:
                logger.debug(f"Line item sheets update failed: {e}")

            return {
                "status": "success",
                "invoice_id": invoice_id,
                "line_items": line_items,
                "total_items": len(line_items),
            }

        # Parse results — Gemini returns {field: {value, bbox}} or {field: "value"}
        found = {}
        found_annotations = []
        not_found = []

        # Get Document AI's full text for OCR-based position matching
        full_text = invoice.get("extracted_data", {}).get("full_text", "")

        for k, v in extracted.items():
            if v is None:
                not_found.append(k)
                continue

            value = v["value"] if isinstance(v, dict) and "value" in v else str(v)
            gemini_bbox = v.get("bbox") if isinstance(v, dict) else None
            found[k] = value

            # Try to find bounding box — OCR match first, Gemini fallback
            bbox = None
            bbox_source = None

            # Priority 1: Match against Document AI OCR text positions
            if full_text and value:
                ocr_bbox = _find_text_in_ocr(invoice, value)
                if ocr_bbox:
                    bbox = ocr_bbox
                    bbox_source = "docai_ocr"

            # Priority 2: Use Gemini's approximate bbox
            if not bbox and gemini_bbox and len(gemini_bbox) == 4:
                x1, y1, x2, y2 = gemini_bbox
                bbox = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                bbox_source = "gemini_approx"

            if bbox:
                found_annotations.append({
                    "type": f"custom_{k}",
                    "value": value,
                    "bbox": bbox,
                    "confidence": 0.95 if bbox_source == "docai_ocr" else 0.6,
                    "source": bbox_source,
                })

        # Store in invoice
        if "custom_fields" not in invoice:
            invoice["custom_fields"] = {}
        invoice["custom_fields"].update(found)

        # Add annotations to the invoice's list
        if found_annotations:
            if "extracted_data" in invoice:
                existing = invoice["extracted_data"].get("annotations", [])
                invoice["extracted_data"]["annotations"] = existing + found_annotations

        # Store Layer 2 fields separately — never touch Document AI columns.
        # Prefix with "custom_" but use the SAME base name as Document AI
        # so columns are easy to match:
        #   Document AI: "supplier_name" → Sheet column "Vendor"
        #   Layer 2:     "custom_supplier_name" → Sheet column "Custom Vendor"
        if "extracted_data" in invoice:
            for fname, fvalue in found.items():
                invoice["extracted_data"]["fields"][f"custom_{fname}"] = {
                    "value": str(fvalue),
                    "confidence": 0.85,
                    "source": "gemini_vision",
                }

        # Persist to Google Sheets (add custom fields as new columns)
        try:
            from .sheets import add_invoice_to_sheet
            from ..config import SHEETS_ENABLED
            if SHEETS_ENABLED and "extracted_data" in invoice:
                add_invoice_to_sheet(
                    invoice_id=invoice_id,
                    extracted_data=invoice["extracted_data"],
                    filename=invoice.get("filename"),
                )
                logger.info(f"Layer 2 fields for {invoice_id} saved to Sheets")
        except Exception as e:
            logger.debug(f"Sheets update for custom fields failed: {e}")

        # Auto-record each found field as an implicit label for uptraining
        from .auto_uptrainer import record_extraction
        full_text = invoice.get("extracted_data", {}).get("full_text", "")
        for fname, fvalue in found.items():
            record_extraction(
                invoice_id=invoice_id,
                field_name=fname,
                extracted_value=str(fvalue),
                image_path=invoice.get("filepath", ""),
                mime_type=invoice.get("mime_type", ""),
                full_text=full_text,
            )

        result = {
            "status": "success",
            "invoice_id": invoice_id,
            "fields_found": found,
            "fields_not_found": not_found,
            "total_requested": len(fields_to_extract),
            "total_found": len(found),
        }

        logger.info(
            f"Custom extraction for {invoice_id}: "
            f"{len(found)}/{len(fields_to_extract)} fields found"
        )

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        return {
            "status": "error",
            "message": f"Gemini returned invalid JSON. Raw response: {raw_text[:500]}",
        }
    except Exception as e:
        logger.error(f"Custom extraction failed: {e}")
        return {
            "status": "error",
            "message": f"Extraction failed: {str(e)}",
        }


def list_industry_fields(industry: str = "") -> dict:
    """List available industry-specific field presets.

    Shows what custom fields can be extracted for each industry type.
    Use this to know what fields are available before calling extract_custom_fields.

    Args:
        industry: Specific industry to show fields for, or empty for all.

    Returns:
        Dictionary of industry presets with their field lists.
    """
    if industry and industry in INDUSTRY_FIELDS:
        preset = INDUSTRY_FIELDS[industry]
        return {
            "industry": industry,
            "description": preset["description"],
            "fields": preset["fields"],
            "total_fields": len(preset["fields"]),
        }

    return {
        "industries": {
            k: {
                "description": v["description"],
                "field_count": len(v["fields"]),
                "sample_fields": v["fields"][:5],
            }
            for k, v in INDUSTRY_FIELDS.items()
        },
        "usage": "Call extract_custom_fields(invoice_id, ['industry_name']) to use a preset, "
                 "or specify individual field names.",
    }
