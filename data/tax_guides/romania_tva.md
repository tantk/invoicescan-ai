# Romania — TVA (Taxa pe Valoarea Adăugată) Guide

## Overview

Romania's Value Added Tax, known as TVA (Taxa pe Valoarea Adăugată), is a consumption tax on the supply of goods and services within Romania and on imports. It is administered by **ANAF** (Agenția Națională de Administrare Fiscală — National Agency for Fiscal Administration). Effective August 1, 2025, the standard rate increased from 19% to 21%, and the reduced rates were consolidated to 11% (replacing the former 5% and 9% rates). Romania has one of the most advanced mandatory e-invoicing systems in the EU, operating the **RO e-Factura** clearance system since January 2024 for B2B and since January 2025 for B2C transactions.

## Tax Rates

- **Standard rate: 21%** (effective August 1, 2025; previously 19%) — applies to most goods and services
- **Reduced rate: 11%** (effective August 1, 2025; replaces former 5% and 9%) — applies to:
  - Food and non-alcoholic beverages
  - Medicines
  - Water supply services
  - Agricultural inputs (seeds, fertilizers, pesticides)
  - Books, newspapers, and periodicals (print and digital)
  - Access to cultural sites (museums, theatres, monuments)
  - Firewood and wood products for heating
  - Thermal energy for residential heating
  - Social housing (under certain thresholds)
  - Accommodation and restaurant services
  - Baby food and baby hygiene products
- **Transitional rate: 9%** — continues to apply to certain housing supplies until August 2026
- **Zero-rated (0%)**:
  - Intra-EU supplies of goods (with valid VAT number of the buyer)
  - Exports of goods outside the EU
  - International transport services
  - Supplies related to vessels and aircraft used in international traffic
- **Exempt (without right of deduction)**:
  - Financial and insurance services
  - Medical and dental services
  - Education services
  - Postal services by the national postal operator
  - Leasing of residential property
  - Cultural, sporting, and religious services (under certain conditions)
  - Social welfare services

## Tax ID Format

**CUI/CIF (Codul Unic de Înregistrare / Codul de Identificare Fiscală)**

- **Format:** 2 to 10 digits, optionally preceded by the prefix "RO" for VAT purposes
- **Structure:** The numeric CUI/CIF is assigned upon company registration. For VAT-registered entities, the prefix "RO" is added (e.g., `RO12345678`).
- **Individuals:** 13-digit CNP (Cod Numeric Personal — personal numeric code)
- **Example:** `RO12345678` (VAT-registered company) or `12345678` (non-VAT company)
- **Verification:** [ANAF RO e-Factura Portal](https://www.anaf.ro/anaf/internet/ANAF/informatii_publice/verificare) or [EU VIES System](https://ec.europa.eu/taxation_customs/vies/)

## Invoice Requirements

Under the RO e-Factura system, invoices must be in XML format (UBL 2.1 or CII, compliant with EN 16931 / RO_CIUS) and include:

1. Invoice number (unique sequential)
2. Date of issue
3. Date of supply/delivery (if different from issue date)
4. Supplier's full legal name
5. Supplier's CUI/CIF (with "RO" prefix if VAT-registered)
6. Supplier's registered address
7. Supplier's Trade Register number
8. Buyer's full legal name
9. Buyer's CUI/CIF (with "RO" prefix if VAT-registered)
10. Buyer's registered address
11. Description of goods or services
12. Quantity and unit of measure
13. Unit price (exclusive of TVA)
14. Discounts or rebates (if applicable)
15. Taxable amount per TVA rate or exemption category
16. TVA rate(s) applied (21%, 11%, 9%, or 0%)
17. TVA amount (expressed in RON — Romanian Leu)
18. Total amount inclusive of TVA
19. Currency (if not RON, exchange rate must be indicated; TVA must be expressed in RON regardless)
20. Reference to exemption provision (if applicable — article of the Fiscal Code)
21. "Self-billing" indication (if applicable)
22. "Reverse charge" indication (if applicable)
23. Reference to original invoice (for credit/debit notes)

## E-Invoicing

- **Status:** Mandatory for all domestic transactions.
  - **B2B:** Mandatory since January 1, 2024 for Romanian-established businesses and non-established VAT-registered taxpayers
  - **B2C:** Mandatory since January 1, 2025
  - **E-reporting (2026):** From January 1, 2026, invoices from Romanian taxable persons to VAT-registered customers without a fixed establishment in Romania must be reported through the system
- **Platform:** RO e-Factura, operated by ANAF, accessible via the SPV (Spațiul Privat Virtual — Virtual Private Space).
- **Format:** XML (UBL 2.1 or CII syntax), compliant with European standard EN 16931 and Romanian national specifications (RO_CIUS).
- **Model:** Clearance — invoices must be uploaded to the RO e-Factura system, where ANAF validates them before they are made available to the recipient.
- **Submission deadline:** 5 working days from the date of issuance (changed from 5 calendar days as of January 2026).
- **Download deadline:** Recipients must download invoices within 60 days.
- **Small taxpayer grace period:** Full enforcement for small taxpayers (turnover below EUR 500,000) postponed until July 1, 2026, though the system itself remains mandatory.
- **e-TVA (pre-populated returns):** ANAF generates pre-populated VAT returns based on e-Factura data. The grace period for discrepancies ended July 1, 2025 — penalties now apply for mismatches.
- **e-Transport:** Complementary system for tracking physical movement of goods within Romania (separate from e-Factura but part of the overall digital compliance framework).

## Key Rules

- **Rate change transition:** The standard rate increased to 21% on August 1, 2025. Invoices issued for supplies made before that date at 19% remain valid. Businesses must ensure correct rate application based on the tax point (not the invoice date).
- **5-working-day submission rule:** Since January 2026, invoices must be transmitted to RO e-Factura within 5 working days (not calendar days) from issuance. Failure results in fines.
- **TVA must be expressed in RON:** Even for foreign currency transactions, the TVA amount must always be stated in Romanian Leu (RON) using the exchange rate on the date of the tax point.
- **Reverse charge mechanism:** Applies to certain domestic supplies (construction services, waste materials, cereals, mobile phones, laptops over EUR 450 per item) and all intra-EU acquisitions. The buyer self-assesses TVA.
- **Input TVA deduction:** Requires valid e-Factura-reported invoices. ANAF cross-references purchase claims against supplier-reported invoices via e-TVA.
- **Pro-rata deduction:** Businesses making both taxable and exempt supplies must calculate a pro-rata percentage for input TVA recovery.
- **Filing:** Monthly TVA returns (Form 300) for businesses with annual turnover above EUR 100,000; quarterly for those below. Due by the 25th of the month following the reporting period.

## Common Pitfalls

1. **Applying the old 19% rate after August 1, 2025** — The standard rate is now 21%. Invoices must reflect the rate applicable at the tax point. Undercharging TVA creates a liability for the supplier.
2. **Submitting invoices after the 5-working-day deadline** — Since January 2026, late submission to RO e-Factura results in fines. Businesses must have automated systems to ensure timely upload.
3. **Not reconciling e-TVA pre-populated returns** — ANAF's pre-populated returns are based on e-Factura data. Discrepancies between your actual return and the pre-populated version trigger audits and penalties (grace period ended July 2025).
4. **Confusing the 11% and 9% transitional rates** — The old 9% rate continues for certain housing supplies until August 2026. Misapplying 11% to a 9% transitional supply (or vice versa) results in incorrect invoicing.
5. **Not downloading received invoices within 60 days** — Invoices in the RO e-Factura system must be downloaded within 60 days. Failure to do so may affect input TVA deduction rights.
6. **Omitting "RO" prefix for VAT-registered entities** — The CUI without the "RO" prefix is not a valid VAT number. Using it on invoices intended for intra-EU transactions will invalidate the transaction's VAT treatment.
7. **Ignoring e-Transport requirements** — Physical movement of certain high-risk goods within Romania must be declared in the e-Transport system. Non-compliance triggers separate fines, even if the e-Factura invoice is correct.
8. **Assuming small taxpayer exemption from the system** — While enforcement penalties for small taxpayers (under EUR 500,000 turnover) are postponed until July 2026, the obligation to use RO e-Factura still exists. Businesses should not wait until the enforcement date to implement the system.
