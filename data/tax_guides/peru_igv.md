# Peru — IGV (Impuesto General a las Ventas) Guide

## Overview

Peru's general sales tax, known as IGV (Impuesto General a las Ventas), is a value-added tax levied on the sale of goods, provision of services, construction contracts, imports, and first sale of real estate. It is administered by **SUNAT** (Superintendencia Nacional de Aduanas y de Administración Tributaria). Effective January 1, 2026, the internal structure of the combined 18% rate was revised under Law No. 32387: IGV was reduced from 16% to 14%, while the IPM (Impuesto de Promoción Municipal) was increased from 2% to 4%. The total combined rate remains 18%. Electronic invoicing (CPE) is mandatory for virtually all taxpayers.

## Tax Rates

- **Standard rate: 18%** (14% IGV + 4% IPM) — applies to most goods and services
- **Reduced rate: 8%** — applies to:
  - Small restaurant, tourism, and hospitality businesses (for fiscal years 2025 and 2026)
  - Reverts to 12% for fiscal year 2027
- **Zero-rated (0%)**:
  - Exports of goods
  - Exports of services (when meeting SUNAT criteria for foreign consumption)
- **Exempt**:
  - Basic foodstuffs (rice, sugar, fresh vegetables, fresh fruits, fresh meats, eggs, milk)
  - Education services (public and private schools, universities)
  - Health services
  - Public transport
  - First sale of real estate (up to 35 UITs value)
  - Insurance (life, accident, and certain agricultural insurance)
  - Books and educational materials
  - Financial services (interest on deposits, certain credit operations)
  - Cultural shows and exhibitions

## Tax ID Format

**RUC (Registro Único de Contribuyentes)**

- **Format:** 11 digits
- **Structure:**
  - Prefix `10` + DNI number + verification digit (individuals with DNI)
  - Prefix `15` + random number + verification digit (individuals with other ID)
  - Prefix `20` + random number + verification digit (legal entities)
- **Example:** `20123456789`
- **Verification:** [SUNAT RUC Consultation](https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp)
- **Note:** Since July 2025, the RUC must be displayed when offering goods and services, including in online advertisements.

## Invoice Requirements

1. Document title (Factura, Boleta de Venta, Nota de Crédito, Nota de Débito)
2. Issuer's legal name (razón social or nombre comercial)
3. Issuer's RUC number
4. Issuer's fiscal address
5. Document serial number and sequential number
6. Date of issue
7. Date of delivery or service completion (if different from issue date)
8. Buyer's legal name and RUC (for Facturas)
9. Buyer's document type and number
10. Description of goods or services with sufficient detail
11. Quantity and unit of measure
12. Unit value (before tax)
13. Total sale value (before tax)
14. Discount amounts (if applicable)
15. IGV amount (broken out separately)
16. Total price including IGV
17. Currency (if not PEN, applicable exchange rate)
18. Digital signature (XML Signature using valid digital certificate)
19. Hash code (resumen) for verification
20. SUNAT authorization or OSE validation response code

## E-Invoicing

- **Status:** Mandatory for all RUC-registered taxpayers (except those under NRUS — Nuevo Régimen Único Simplificado, for whom it remains optional).
- **Format:** UBL 2.1 XML, digitally signed with a valid digital certificate.
- **Platform:** Comprobantes de Pago Electrónicos (CPE) system, with multiple issuance options:
  - SEE-SOL: SUNAT's free online portal
  - SEE-SDC: From the taxpayer's own systems
  - SEE-OSE: Through authorized Electronic Services Operators (OSE)
  - SEE-SFS: Simplified Facturador system for small businesses
- **Validation:** Invoices are submitted to SUNAT or an authorized OSE for validation. The response includes a CDR (Constancia de Recepción) confirming acceptance or rejection.
- **Submission deadline:** Issuers have up to 3 calendar days after the issuance date to send invoices and related notes to SUNAT or the OSE.
- **SIRE (Integrated Electronic Records System):** Mandatory for large taxpayers from January 2026, automating purchase and sales records based on CPE data.
- **Retention:** CPEs and associated CDRs must be retained for a minimum of 5 years from the first day of the year following issuance.

## Key Rules

- **Facturas vs. Boletas de Venta:** Facturas are issued to other businesses (allowing IGV credit). Boletas de Venta are issued to final consumers (no IGV credit). Using the wrong type affects the buyer's tax position.
- **IGV credit requirements:** Input IGV can only be claimed if supported by a valid CPE (electronic invoice) with SUNAT/OSE validation, the expense is necessary for the business, and the IGV is itemized separately on the document.
- **Withholding and perception systems:** SUNAT designates certain large buyers as IGV withholding agents (3% of payment) and certain sellers as perception agents (2% additional charge to unregistered buyers).
- **Spot system (detracciones):** For certain goods and services, the buyer must deposit a percentage of the payment into the seller's Banco de la Nación account before paying the invoice. Non-compliance blocks the buyer's right to claim input IGV.
- **Digital services:** Since January 2025, non-resident providers of digital services must withhold and remit IGV on B2C sales to Peruvian consumers.
- **Monthly filing:** IGV returns are filed monthly via the PDT 621 or Declara Fácil form, with due dates based on the last digit of the RUC.

## Common Pitfalls

1. **Confusing the 14% IGV with the total 18% rate** — The 2026 restructuring changed the internal split (14% IGV + 4% IPM), but invoices must still show the full 18%. Reporting only 14% is an error.
2. **Exceeding the 3-day submission deadline** — Invoices sent to SUNAT or the OSE more than 3 calendar days after issuance may be rejected, leaving the invoice without legal validity.
3. **Failing to comply with detracciones (spot system)** — Not depositing the required percentage into the seller's Banco de la Nación account before payment blocks the buyer's right to claim input IGV.
4. **Issuing Boletas to businesses** — Boletas do not grant the buyer IGV credit. Always issue Facturas when selling to registered taxpayers.
5. **Not maintaining digital certificates** — Digital certificates expire and must be renewed. An expired certificate means the business cannot issue valid CPEs.
6. **Ignoring the OSE validation response (CDR)** — A rejected CDR means the invoice is invalid. Businesses must monitor CDR responses and reissue corrected invoices promptly.
7. **Applying the wrong rate to tourism/hospitality** — The 8% reduced rate for small tourism and hospitality businesses is temporary (2025-2026) and subject to specific eligibility criteria. Misapplying it to ineligible businesses results in underpayment.
8. **Not preparing for SIRE** — Large taxpayers must transition to the Integrated Electronic Records System by January 2026. Failure to comply results in penalties and inability to file VAT returns.
