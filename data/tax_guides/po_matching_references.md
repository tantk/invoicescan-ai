# Purchase Order Matching & Document References

## Three-Way Match
The standard AP verification process:
1. **Purchase Order (PO)** — what was ordered
2. **Goods Receipt / Delivery Note (GRN)** — what was received
3. **Invoice** — what is being billed

All three must agree on: items, quantities, and prices. Discrepancies trigger holds.

### Match Tolerances
| Field | Typical tolerance | Action if exceeded |
|-------|------------------|-------------------|
| Quantity | ±5% or ±1 unit | Hold for review |
| Unit price | ±1-2% or ±$0.01 | Hold for review |
| Total amount | ±$5-50 (varies) | Hold for review |
| Tax amount | Exact match or ±$0.01 | Recalculate |

## Document Types Referenced on Invoices
| Document | Purpose | Format |
|----------|---------|--------|
| **PO Number** | What buyer ordered | PO-2026-0001 |
| **SO Number** | Seller's order reference | SO-88901 |
| **Delivery Note / DN** | Proof of delivery | DN-456789 |
| **Goods Received Note / GRN** | Buyer confirmed receipt | GRN-2026-112 |
| **Packing Slip / Packing List** | What's in the shipment | PS-789012 |
| **Bill of Lading / BOL** | Carrier transport document | BOL-MAEU1234567 |
| **Airway Bill / AWB** | Air freight document | AWB-123-45678901 |
| **Proforma Invoice** | Pre-shipment estimate | PI-2026-0089 |
| **Contract Number** | Agreement reference | CTR-2025-0456 |
| **Work Order / WO** | Service/maintenance order | WO-7890 |
| **Job Number** | Project reference | JOB-2026-045 |
| **Requisition Number** | Internal purchase request | REQ-2026-0234 |
| **Tender/Bid Reference** | Competitive bid number | RFQ-2025-089 |
| **Credit Note** | Reduces amount owed | CN-2026-0012 |
| **Debit Note** | Increases amount owed | DN-2026-0005 |
| **Return Authorization / RMA** | Return merchandise auth | RMA-34567 |

## Invoice Type Codes (UNCL 1001)
| Code | Type | Description |
|------|------|-------------|
| 380 | Commercial Invoice | Standard sales invoice |
| 381 | Credit Note | Reduces amount owed |
| 383 | Debit Note | Increases amount owed |
| 384 | Corrected Invoice | Replaces a previous invoice |
| 386 | Prepayment Invoice | Request for advance payment |
| 389 | Self-Billing Invoice | Buyer-generated invoice |
| 751 | Invoice Information | For information only, not a demand |
| 325 | Proforma Invoice | Estimate/quote, not a demand |

## Quality & Certification References
| Certificate | When needed | Industry |
|-------------|-------------|----------|
| **Mill Test Report (MTR)** | Metal products | Manufacturing, construction |
| **Certificate of Conformity (CoC)** | Product meets standards | All industries |
| **Certificate of Analysis (CoA)** | Chemical/food composition | Chemical, pharma, food |
| **Certificate of Origin (CoO)** | Country where goods made | International trade |
| **Inspection Certificate** | Third-party inspection passed | Construction, manufacturing |
| **Calibration Certificate** | Measuring equipment certified | Engineering, lab equipment |
| **Material Safety Data Sheet (MSDS/SDS)** | Hazardous materials | Chemical, manufacturing |
| **ISO 9001** | Quality management system | Any industry |
| **EN 10204 Type 2.1/3.1/3.2** | Material certificate types | Steel/metals industry |

## Product Classification Codes
| System | Full Name | Digits | Used For |
|--------|-----------|--------|----------|
| **HS Code** | Harmonized System | 6-10 | International customs/tariff |
| **HSN Code** | Harmonized System Nomenclature | 4-8 | India GST |
| **SAC Code** | Services Accounting Code | 6 | India GST (services) |
| **UNSPSC** | UN Standard Products & Services | 8 | Procurement classification |
| **CPV** | Common Procurement Vocabulary | 8+1 | EU public procurement |
| **GTIN/EAN** | Global Trade Item Number | 8-14 | Product barcode/identifier |
| **UPC** | Universal Product Code | 12 | US/Canada retail |
| **NDC** | National Drug Code | 10 | US pharmaceuticals |
| **CAS Number** | Chemical Abstracts Service | Variable | Chemical identification |
| **UN Number** | UN Dangerous Goods | 4 | Hazardous materials transport |

## Red Flags
- Invoice references a PO that doesn't exist
- Quantity on invoice exceeds PO quantity by more than tolerance
- Invoice total exceeds PO total
- Multiple invoices referencing the same PO (potential duplicate)
- No PO reference on a B2B invoice (may violate buyer's policy)
- Credit note issued without referencing the original invoice
- Invoice date before PO date (can't invoice before ordering)
