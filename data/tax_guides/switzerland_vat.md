# Switzerland — MWST/TVA/IVA (Mehrwertsteuer) Guide

## Overview
Switzerland's VAT is known by different names in its official languages: MWST (Mehrwertsteuer) in German, TVA (Taxe sur la Valeur Ajoutee) in French, and IVA (Imposta sul Valore Aggiunto) in Italian. It is administered by the Federal Tax Administration (Eidgenossische Steuerverwaltung / ESTV, or Administration Federale des Contributions / AFC). Switzerland is **not an EU member state** and does not follow EU VAT Directives — it has its own independent VAT legislation under the Federal Act on Value Added Tax (MWSTG/LTVA). The rates are significantly lower than most European countries.

## Tax Rates
- **Standard rate: 8.1%** (Normalsatz) — applies to most goods and services
- **Reduced rate: 2.6%** (reduzierter Satz) — food and non-alcoholic beverages (excluding restaurant/catering), medications, books and newspapers (print), water supply, agricultural inputs (seeds, plants, animal feed)
- **Special rate: 3.8%** (Sondersatz) — accommodation/lodging services (including breakfast if included in room rate)
- **Zero-rated (0%)**: Exports of goods, services provided abroad with place of supply outside Switzerland, international transport
- **Exempt** (no VAT, no input credit): Healthcare services, education, financial services and insurance, residential rental, cultural services by public institutions, postal services (Swiss Post universal service), sports services by non-profit organizations, gambling and lotteries

### Rate History and Future Changes
- Rates were increased on January 1, 2024 (from 7.7% to 8.1%, 2.5% to 2.6%, 3.7% to 3.8%) to fund the AVS 21 pension reform
- A proposed further increase to 8.8% standard rate (to fund a 13th monthly pension payment) has been **delayed from 2026 to 2028**, pending parliamentary approval and a public referendum

## Tax ID Format
- **UID (Unternehmens-Identifikationsnummer / Enterprise Identification Number)**:
  - Format: `CHE-XXX.XXX.XXX` (MWST/TVA/IVA)
  - Full VAT format: `CHE-123.456.789 MWST` (German), `CHE-123.456.789 TVA` (French), or `CHE-123.456.789 IVA` (Italian)
  - Example: `CHE-116.281.710 MWST`
  - The UID is a 9-digit number with a standard prefix (CHE) and suffix indicating the tax type
- **Old format** (still occasionally seen): 6-digit number, e.g., `123'456`
- Verify at: https://www.uid.admin.ch (UID register) or https://www.estv.admin.ch

## Invoice Requirements
1. Full name and address of the supplier
2. Supplier's UID number with MWST/TVA/IVA suffix
3. Full name and address of the recipient/buyer
4. Invoice date (Rechnungsdatum)
5. Unique invoice number (Rechnungsnummer)
6. Date of supply or service performance (if different from invoice date)
7. Description of goods or services (nature, quantity, scope)
8. Unit price (net of MWST)
9. Net amount per tax rate
10. MWST rate applied (8.1%, 2.6%, 3.8%)
11. MWST amount per rate
12. Total gross amount (including MWST)
13. For exempt supplies: reference to the legal provision or notation "von der Steuer ausgenommen"
14. For reverse charge: notation indicating the recipient is liable for the tax
15. Payment terms

**Timing**: Invoices must be issued within **6 months** of the supply of goods or provision of services.

### Simplified Invoice (up to CHF 400 including MWST)
- Supplier name and UID
- Date
- Description of goods/services
- Total amount including MWST
- MWST rate

## E-Invoicing
- **B2G**: The Swiss federal government accepts e-invoices and encourages their use, but there is **no general B2G e-invoicing mandate**
- **B2B**: No mandatory e-invoicing — paper, PDF, and structured electronic formats are all accepted
- **Formats**: No single mandated format; commonly used standards include:
  - **swissDECODE / eBill**: Swiss domestic payment and invoicing standard integrated with the banking system
  - **QR-bill (QR-Rechnung)**: Since October 2022, all Swiss payment slips use QR codes — the QR-bill has replaced traditional payment slips (orange/red ESR/BVR slips)
  - **ZUGFeRD/Factur-X**: Accepted and gaining adoption, though not mandated
  - **Peppol**: Switzerland has joined the Peppol network; adoption is growing but not mandatory
- **Archiving**: Invoices and business records must be retained for **10 years** in Switzerland

## Key Rules
- **Registration threshold**: CHF 100,000 annual worldwide turnover from taxable or zero-rated supplies. Below the threshold, voluntary registration is possible.
- **Non-resident businesses**: Must register if providing taxable supplies in Switzerland, regardless of turnover — no threshold for foreign businesses (effective since January 1, 2018)
- **Filing frequency**: Quarterly (default) or semi-annually (upon request). Monthly filing is not standard but can be arranged.
- **Filing deadline**: 60 days after the end of the reporting period
- **Net tax rate method (Saldosteuersatzmethode)**: Simplified method available for businesses with annual turnover below CHF 5,005,000 and annual tax liability below CHF 103,000 — flat-rate percentage applied to turnover instead of tracking input VAT
- **Assessment method**: Effective method (actual input VAT deduction) is the default; net tax rate and flat-rate methods are alternatives
- **Reverse charge (Bezugsteuer)**: Applies to services received from non-resident suppliers if the Swiss recipient is VAT-registered. Threshold: CHF 10,000 per year from a single foreign supplier.
- **Import VAT**: Collected by the Federal Customs Administration (BAZG/OFDF) at the border. Can be deducted as input VAT on the MWST return if for business purposes.
- **Place of supply rules**: Follow Swiss MWSTG, which differs from EU rules in certain areas (e.g., different treatment for telecommunications and electronic services)
- **Interest rates (2026)**: 4% on late VAT payments and refunds; 0% on advance payments

## Common Pitfalls
1. **Assuming EU VAT rules apply**: Switzerland is not in the EU — EU reverse charge, intra-community supply rules, VIES, and OSS do not apply. Each cross-border transaction with EU countries is treated as an import/export.
2. **UID suffix confusion**: The UID must include the correct suffix (MWST, TVA, or IVA depending on language region) — using just the number without the suffix is technically incomplete
3. **CHF 100,000 threshold misunderstanding**: The threshold is based on **worldwide** turnover, not just Swiss turnover — a foreign business with global revenue above CHF 100,000 making even small taxable supplies in Switzerland must register
4. **QR-bill compliance**: Since 2022, all payment slips must be QR-bills — using old ESR/BVR orange or red slips is no longer valid
5. **Net tax rate method limitations**: Businesses using this simplified method cannot deduct actual input VAT and cannot issue invoices showing VAT separately (only a VAT-inclusive total) — switching methods is restricted
6. **Cross-border e-commerce**: Digital services to Swiss consumers may trigger VAT registration obligations — Switzerland has its own rules for foreign providers of electronic services (similar to but not the same as EU rules)
7. **Mixed supplies at different rates**: Failing to separate 8.1%, 2.6%, and 3.8% items on a single invoice — each rate must be shown distinctly
8. **10-year retention**: Switzerland requires 10-year document retention, longer than many countries — businesses sometimes destroy records after 7 years based on other jurisdictions' rules
