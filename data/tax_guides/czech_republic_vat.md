# Czech Republic — DPH (Dan z Pridane Hodnoty) Guide

## Overview
The Czech Republic's VAT, known as DPH (Dan z pridane hodnoty), is administered by the Financni sprava (Financial Administration / Czech Tax Authority). The Czech Republic simplified its VAT rate structure effective January 1, 2024, merging two reduced rates (15% and 10%) into a single 12% reduced rate. The system follows EU VAT Directives with Czech-specific implementations.

## Tax Rates
- **Standard rate: 21%**
- **Reduced rate: 12%** (merged from the former 15% and 10% rates on January 1, 2024) — applies to:
  - Food products (excluding alcoholic beverages and certain luxury foods)
  - Non-alcoholic beverages
  - Water supplies
  - Medicines and medical devices
  - Books (print and e-books), newspapers, and periodicals
  - Accommodation services
  - Restaurant and catering services (food, not alcohol)
  - Domestic passenger transport
  - Admission to cultural, sporting, and entertainment events
  - Firewood and pellets
  - Cut flowers and plants
  - Children's car seats
  - Hairdressing services
- **Zero-rated (0%)**: Exports of goods, intra-EU supplies of goods (with valid buyer VAT ID), international transport
- **Exempt (no VAT, no input credit)**: Financial and insurance services, healthcare, education, residential property rental (unless opted to tax), postal services (universal), social services, certain cultural services by public institutions, transfer of immovable property (after 5 years)

## Tax ID Format
- **DIC** (Danove identifikacni cislo / Tax Identification Number): Format `CZ` + 8, 9, or 10 digits
  - Legal entities: `CZ` + 8 digits (ICO / company registration number)
  - Individuals: `CZ` + 9 or 10 digits (based on birth number / rodne cislo)
  - Example: `CZ12345678`
- **ICO** (Identifikacni cislo osoby / Company Registration Number): 8 digits
  - Example: `12345678`
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES) or https://adisspr.mfcr.cz/dpr/DphReg

## Invoice Requirements
### Full VAT Invoice (danovy doklad)
1. Invoice date (datum vystaveni)
2. Unique sequential invoice number (evidencni cislo)
3. Seller's full name, address, and DIC
4. Buyer's full name, address, and DIC (if VAT-registered)
5. Date of taxable supply (datum uskutecneni zdanitelneho plneni) — mandatory, cannot be omitted
6. Description of goods or services
7. Quantity, unit of measure, and unit price (exclusive of DPH)
8. Net amount per DPH rate
9. DPH rate(s) applied (21%, 12%)
10. DPH amount per rate
11. Total amount inclusive of DPH
12. For exempt supplies: reference to the applicable Czech VAT Act (ZDPH) provision or EU VAT Directive article
13. For reverse charge: "Dan odvede zakaznik" notation
14. For intra-EU: both parties' DIC numbers and reference to exemption
15. For simplified tax document: "Zjednoduseny danovy doklad" label

### Simplified Tax Document (zjednoduseny danovy doklad, for supplies up to CZK 10,000 including DPH)
1. Seller's name and DIC
2. Invoice date
3. Description of goods or services
4. Total amount inclusive of DPH
5. DPH rate

## Control Statement (Kontrolni Hlaseni)
- Mandatory for all VAT-registered entities since January 1, 2016
- Detailed transaction-level reporting to the Financial Administration
- **Filing frequency**: Monthly for legal entities; quarterly for individuals filing quarterly VAT returns
- **Due date**: 25th day of the month following the reporting period
- Reports: issued invoices over CZK 10,000 (with buyer DIC), received invoices over CZK 10,000, and all domestic reverse-charge transactions
- Penalties for non-filing: CZK 1,000 (late), up to CZK 50,000 (repeated failures)

## E-Invoicing
- **B2G**: Mandatory for invoices to public contracting authorities above EU procurement thresholds — must comply with EN 16931 standard
- **B2B**: Not yet mandatory — no current B2B e-invoicing mandate
- **ISDOC**: Czech national e-invoice standard (Information System Document) — widely used domestically but not mandated for B2B
- **Peppol**: Supported for B2G transactions
- **Future plans**: Czech Republic is expected to align with EU ViDA requirements, with mandatory B2B e-invoicing anticipated around 2030
- **Archiving**: Invoices must be stored for **10 years**

## Key Rules
- **Registration threshold**: CZK 2,000,000 (approx. EUR 80,000) annual taxable turnover for domestic businesses. No threshold for non-resident businesses — registration required from the first taxable supply.
- **EU distance selling threshold**: EUR 10,000 (common EU-wide threshold)
- **Filing frequency**: Monthly for most businesses; quarterly for businesses with annual turnover under CZK 10,000,000 (and who elected quarterly filing at registration)
- **Payment deadline**: 25th day of the month following the reporting period
- **Tax point**: Generally the date of delivery of goods or completion of services; for advance payments, the date the payment is received
- **Reverse charge (preneseni danove povinnosti)**: Applies to construction services, certain waste/scrap sales, services from non-resident suppliers, emission allowances, and real estate transfers (where applicable)
- **Unreliable taxpayer (nespolehlivy platce)**: The Financial Administration publicly lists "unreliable" VAT payers — transactions with these entities create joint liability for the buyer for unpaid VAT
- **Intrastat**: Reporting required for intra-EU goods trade above thresholds
- **EC Sales List**: Required for intra-EU supplies of goods and services

## Common Pitfalls
1. **Rate consolidation**: Since January 2024, there is only ONE reduced rate (12%) — do not apply the old 15% or 10% rates
2. **Control Statement compliance**: Missing or late Control Statements trigger automatic penalties — this is separate from the VAT return itself
3. **Date of supply mandatory**: The datum uskutecneni zdanitelneho plneni must always appear on the invoice — omitting it invalidates the document for input tax purposes
4. **Unreliable taxpayer risk**: Check the public register before transacting with new suppliers — the buyer may become jointly liable for VAT if the supplier is listed as "unreliable"
5. **DIC vs. ICO**: The DIC (tax ID with CZ prefix) is used for VAT purposes; the ICO (company registration number) is for corporate registration — invoices must show the DIC
6. **Quarterly vs. monthly filing**: Businesses crossing the CZK 10 million turnover threshold must switch to monthly filing — missing this transition creates compliance issues
7. **Reverse charge on construction**: Domestic construction services between VAT payers use reverse charge — the supplier does NOT charge DPH; the buyer self-accounts
8. **Non-resident registration**: No threshold — foreign businesses must register from the first taxable supply in the Czech Republic
