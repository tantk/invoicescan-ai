# Germany — VAT (Umsatzsteuer) & E-Invoicing Guide

## Overview
Germany's VAT (Umsatzsteuer/USt or Mehrwertsteuer/MwSt) is the largest source of tax revenue. Germany is transitioning to mandatory B2B e-invoicing starting January 1, 2025.

## Tax Rates
- **Standard rate: 19%**
- **Reduced rate: 7%** (food, books, newspapers, public transport, hotel accommodation, cultural events, agricultural products, medical aids, flowers/plants)
- **0%**: Intra-community supplies, exports
- **Exempt**: Financial services, insurance, residential rent, medical services, education

## VAT Number Formats
- **Steuernummer** (Tax Number): varies by state, 10-13 digits (e.g., `12/345/67890`)
- **USt-IdNr** (VAT ID for EU): `DE` + 9 digits: `DE123456789`
- Both may appear on invoices; USt-IdNr required for intra-EU trade

## Invoice Requirements (§14 UStG)
### Full Invoice
1. Full name and address of seller
2. Full name and address of buyer
3. Seller's tax number (Steuernummer) OR VAT ID (USt-IdNr)
4. Invoice date
5. Unique sequential invoice number
6. Quantity and type of goods / scope of services
7. Date of supply (if different from invoice date)
8. **Net amount per tax rate**
9. **Tax rate and tax amount per rate** (19% and 7% shown separately)
10. **Gross total**
11. Any agreed reductions (discounts, rebates)
12. Advance payments received
13. For reverse charge: "Steuerschuldnerschaft des Leistungsempfängers" (liability shifts to recipient)
14. For intra-EU: both parties' VAT IDs + reference to exemption
15. For small business (§19 UStG): "Kein Ausweis der Umsatzsteuer" notation

### Simplified Invoice (≤€250 gross)
- Seller name and address
- Date
- Description
- Gross amount and tax rate
- Note: buyer info not required

## E-Invoicing (XRechnung / ZUGFeRD)
### B2G (already mandatory)
- XRechnung format required for all federal government invoices
- XML-only (no visual PDF component)
- Based on EN 16931 (UBL or CII syntax)

### B2B (mandatory from January 1, 2025)
- All B2B invoices must be in structured electronic format
- **Accepted formats**: XRechnung, ZUGFeRD (Factur-X), any EN 16931 compliant format
- **Transition periods**:
  - 2025–2026: Can still send paper/PDF, but must be ABLE to receive e-invoices
  - 2027: Must send e-invoices (exception: <€800,000 revenue can use PDF until 2028)
  - 2028: Full mandatory for all

### ZUGFeRD / Factur-X
- Hybrid format: PDF/A-3 with embedded XML
- Five profiles: Minimum, Basic, Comfort (EN16931), Extended, XRechnung
- Human-readable AND machine-readable
- Franco-German cooperation (Factur-X = French name)

## Reverse Charge (§13b UStG)
Applies to:
- Services from foreign businesses
- Construction work (subcontractor to main contractor)
- Scrap metal supplies
- Certain clean energy certificates
- Invoice must state: "Steuerschuldnerschaft des Leistungsempfängers"

## Kleinunternehmer (Small Business Exemption)
- Revenue ≤€22,000 previous year AND ≤€50,000 current year
- No VAT charged, no input credits
- Must state on invoice: not subject to VAT per §19 UStG

## Common Pitfalls
- Missing mandatory invoice fields → buyer loses input credit
- Not separating 19% and 7% items on the same invoice
- Reverse charge: forgetting the required notation
- ZUGFeRD profile too low (Minimum/Basic) for EN 16931 compliance
- Not ready to receive e-invoices by 2025
- Steuernummer vs USt-IdNr confusion (need USt-IdNr for EU trade)
