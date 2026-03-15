# Hungary — AFA (Altalanos Forgalmi Ado) Guide

## Overview
Hungary's VAT, known as AFA (Altalanos Forgalmi Ado), is administered by NAV (Nemzeti Ado- es Vamhivatal / National Tax and Customs Administration). Hungary has the highest standard VAT rate in the world at 27%. The system follows EU VAT Directives with Hungarian-specific implementations, including a pioneering real-time invoice reporting (RTIR) system.

## Tax Rates
- **Standard rate: 27%** (THE HIGHEST VAT RATE IN THE WORLD)
- **Reduced rate: 18%** — certain food products sold for on-premises consumption (restaurant/catering food services), dairy products, bakery products, flour, certain cereal products
- **Reduced rate: 5%** — basic food items (meat, eggs, milk, bread), books (print and e-books), newspapers and periodicals, medicines, medical devices, new residential housing (first supply, under certain size thresholds), district heating, internet access services, live music performances, hotel accommodation
- **Zero-rated (0%)**: Exports of goods, intra-EU supplies of goods (with valid buyer VAT ID), international transport
- **Exempt (no VAT, no input credit)**: Financial and insurance services, healthcare, education, residential property rental (unless opted to tax), postal services (universal), social services, certain cultural services

## Tax ID Format
- **Adoszam** (Tax number): 11 digits, format `XXXXXXXX-X-XX`
  - First 8 digits: taxpayer ID
  - 9th digit: VAT status code (1 = subject to VAT, 2 = exempt, 3 = simplified, 5 = group member)
  - Last 2 digits: county code (where registered)
  - Example: `12345678-1-42`
- **Kozossegi adoszam** (EU VAT number): Format `HU` + first 8 digits of the adoszam
  - Example: `HU12345678`
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES) or https://nav.gov.hu

## Invoice Requirements
### Full VAT Invoice (szamla)
1. Invoice date (kelt)
2. Unique sequential invoice number (szamlaszam)
3. Seller's full name, address, and adoszam
4. Buyer's full name, address, and adoszam
5. Buyer's EU VAT number (for intra-EU transactions)
6. Date of supply (teljesites napja) — mandatory, cannot be omitted
7. Date of payment (if different from supply date)
8. Description of goods or services
9. Quantity, unit of measure, and unit price (exclusive of AFA)
10. Net amount per AFA rate
11. AFA rate(s) applied (27%, 18%, 5%)
12. AFA amount per rate
13. Total amount inclusive of AFA
14. For exempt supplies: reference to the applicable Hungarian VAT Act section or EU VAT Directive provision
15. For reverse charge: "Fordított adózás" notation
16. For intra-EU: "Közösségen belüli termékértékesítés" notation with both parties' VAT IDs
17. For cash accounting scheme: "Pénzforgalmi elszámolás" notation
18. For self-billing: "Önszámlázás" notation

### Simplified Invoice (egyszerusitett szamla, for supplies up to HUF 100,000)
1. Seller's name and adoszam
2. Invoice date
3. Sequential invoice number
4. Description of goods or services
5. Total amount inclusive of AFA
6. AFA rate

## Real-Time Invoice Reporting (RTIR) — Online Szamla
Hungary's NAV operates a mandatory real-time invoice data reporting system:
- **Scope**: All invoices — B2B, B2C, export, and intra-community — must be reported
- **Reporting deadline**: At the time of invoicing or within 24 hours via automated system integration
- **XML schema**: Version 3.0 mandatory (version 2.0 support ended May 15, 2025)
- **Data reported**: Full invoice content including line-item details, tax rates, amounts, and parties
- **Received invoices**: From 2026, domestic taxpayers must also report received invoices to NAV within 5 days of receipt
- **Buyer status report**: Buyers are required to submit a status report (acceptance/rejection of invoice data) by their VAT return deadline
- **ANYK system shutdown**: The legacy ANYK filing system will shut down December 31, 2026 — all submissions must use NAV's modern data-based platforms from January 1, 2027

## E-Invoicing
- **B2G**: Mandatory — public procurement invoices must be submitted electronically
- **B2B**: Real-time reporting (RTIR) is mandatory; full structured e-invoicing mandate is under development, aligned with EU ViDA
- **Future ViDA alignment**: Hungary is preparing a mandatory structured e-invoicing system aligned with the EU ViDA (VAT in the Digital Age) initiative — public consultation was held in early 2026
- **Archiving**: Invoices must be stored for **10 years**

## Key Rules
- **Registration threshold**: No threshold for foreign businesses — registration required from the first taxable supply in Hungary. Domestic businesses with only exempt supplies are not required to register.
- **Filing frequency**: Monthly for most businesses; quarterly for businesses with annual turnover under HUF 50 million and no intra-EU transactions; annually for small taxpayers under the simplified regime
- **Tax point (teljesites idopont)**: Strict rules — generally the date of delivery/service completion; for continuous supplies, the due date of payment; for advance payments, the date the payment is received
- **Reverse charge (forditott adozas)**: Applies to construction services, certain waste/scrap sales, services from non-resident suppliers, and real estate transfers (where opted)
- **Cash accounting scheme (penzforgalmi elszamolas)**: Available for businesses with annual turnover under HUF 125 million — VAT becomes due only when payment is received
- **Intrastat**: Reporting required for intra-EU goods trade above thresholds
- **EC Sales List**: Required for intra-EU supplies of goods and services

## Common Pitfalls
1. **27% is the world's highest**: Do not assume a lower rate — Hungary's standard rate exceeds all other countries
2. **Three VAT rates**: Correctly distinguishing between 27%, 18%, and 5% is critical — restaurant food is 18%, grocery meat/bread is 5%, and most other goods are 27%
3. **RTIR compliance**: All invoices must be reported to NAV in real time — failure incurs fines of up to HUF 500,000 per invoice
4. **XML version 3.0**: Version 2.0 is no longer accepted — ensure ERP/invoicing systems use the current 3.0 schema
5. **Date of supply mandatory**: Unlike some countries, the teljesites idopont must always appear on the invoice — it cannot be omitted even if it matches the invoice date
6. **Received invoice reporting**: New 2026 requirement — buyers must report received invoices within 5 days
7. **ANYK shutdown**: The legacy filing system shuts down December 31, 2026 — migrate to NAV's data-based platforms before this date
8. **Adoszam structure**: The 9th digit indicates VAT status — an adoszam with "2" in position 9 means the entity is VAT-exempt, which affects reverse charge and input tax recovery
